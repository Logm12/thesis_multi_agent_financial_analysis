import os
import time
import json
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from core.config import ROUTER_MODEL, SYNTHESIZER_MODEL, OLLAMA_BASE_URL
from dotenv import load_dotenv

load_dotenv()

# Rate limiting settings for NVIDIA NIM (Free tier: ~10 requests per minute)
NIM_RATE_LIMIT_DELAY = 6.0  # seconds between calls
last_call_time = 0.0

def wait_for_rate_limit():
    global last_call_time
    now = time.time()
    elapsed = now - last_call_time
    if elapsed < NIM_RATE_LIMIT_DELAY:
        sleep_time = NIM_RATE_LIMIT_DELAY - elapsed
        print(f"[NIM Client] Rate limit protection: sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)
    last_call_time = time.time()

def get_nim_llm(model_name: str, temperature: float = 0.0, api_key: Optional[str] = None) -> ChatOpenAI:
    """
    Returns a ChatOpenAI client configured for NVIDIA NIM, falling back to OpenAI
    or local Ollama if NVIDIA keys are not available or requests fail.
    """
    nvidia_key = api_key or os.getenv("NVIDIA_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Route OpenAI models directly to ChatOpenAI instead of NVIDIA NIM API
    if "gpt" in model_name.lower() or not nvidia_key:
        print(f"[NIM Client] Routing {model_name} directly to OpenAI client.")
        return ChatOpenAI(
            model=model_name if "gpt" in model_name.lower() else "gpt-4o-mini",
            temperature=temperature,
            api_key=openai_key
        )
        
    class RateLimitedChatOpenAI(ChatOpenAI):
        def invoke(self, *args, **kwargs):
            wait_for_rate_limit()
            try:
                return super().invoke(*args, **kwargs)
            except Exception as e:
                print(f"[NIM Client] NIM invocation failed: {e}. Attempting fallback...")
                try:
                    fallback_llm = ChatOllama(
                        base_url=OLLAMA_BASE_URL.replace("/v1", ""),
                        model="qwen2.5-coder-thesis:latest",
                        temperature=temperature
                    )
                    print("[NIM Client] Fallback to Ollama succeeded.")
                    return fallback_llm.invoke(*args, **kwargs)
                except Exception as ollama_err:
                    print(f"[NIM Client] Ollama fallback failed: {ollama_err}. Raising original exception.")
                    raise e
                    
        def with_structured_output(self, schema, **kwargs):
            if "deepseek" in self.model.lower() or "llama" in self.model.lower():
                def structured_fallback(input_data):
                    messages = []
                    # Extract messages from various format types
                    if hasattr(input_data, "to_messages"):
                        messages = input_data.to_messages()
                    elif isinstance(input_data, list):
                        messages = list(input_data)
                    elif isinstance(input_data, dict):
                        # Try to format if input is dict
                        pass
                    
                    schema_json = schema.model_json_schema() if hasattr(schema, "model_json_schema") else schema
                    
                    # Generate a concrete example JSON based on the schema to instruct the model to fill in actual values
                    properties = schema_json.get("properties", {})
                    example_json = {}
                    for prop_name, prop_info in properties.items():
                        if "enum" in prop_info:
                            example_json[prop_name] = prop_info["enum"][0]
                        elif prop_info.get("type") == "string":
                            example_json[prop_name] = "string_value"
                        elif prop_info.get("type") == "integer":
                            example_json[prop_name] = 0
                        elif prop_info.get("type") == "number":
                            example_json[prop_name] = 0.0
                        elif prop_info.get("type") == "boolean":
                            example_json[prop_name] = False
                        else:
                            example_json[prop_name] = ""

                    json_instruction = (
                        f"\n\nYou MUST return a JSON object matching this schema description, populating the keys with actual classification results:\n"
                        f"Schema:\n{json.dumps(schema_json)}\n"
                        f"Example target output structure (populate keys with actual content, do not copy this text):\n{json.dumps(example_json)}\n"
                        f"Do not return the schema definition itself. Return ONLY the populated JSON object. "
                        f"Do not include any thinking or explanation outside the JSON format. "
                        f"Ensure only valid JSON is returned."
                    )
                    
                    # Inject instructions
                    if messages:
                        # Append to system prompt or first message
                        if isinstance(messages[0], SystemMessage):
                            messages[0].content += json_instruction
                        else:
                            messages.insert(0, SystemMessage(content="You are a JSON assistant. Output only JSON." + json_instruction))
                    else:
                        messages = [SystemMessage(content="You are a JSON assistant. Output only JSON." + json_instruction)]
                    
                    try:
                        response = self.invoke(messages)
                        content = response.content
                        
                        # Clean up think blocks and codeblocks
                        if "</think>" in content:
                            content = content.split("</think>")[-1].strip()
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0].strip()
                        content = content.strip()
                        
                        data = json.loads(content)
                        if hasattr(schema, "model_validate"):
                            return schema.model_validate(data)
                        return data
                    except Exception as parse_err:
                        print(f"[NIM Client] Parsing failed: {parse_err}. Retrying with local Ollama fallback...")
                        fallback_llm = ChatOllama(
                            base_url=OLLAMA_BASE_URL.replace("/v1", ""),
                            model="qwen2.5-coder-thesis:latest",
                            temperature=0.0
                        )
                        return fallback_llm.with_structured_output(schema).invoke(input_data)
                return RunnableLambda(structured_fallback)
            else:
                return super().with_structured_output(schema, **kwargs)
                
    return RateLimitedChatOpenAI(
        model=model_name,
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_key,
        temperature=temperature
    )
