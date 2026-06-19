import os
import sys
import shutil
import re
import chainlit as cl
from langchain_core.messages import HumanMessage

# Thêm thư mục src vào path để import các module local
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.graph import app as graph_app, ingest_pdf
from core.config import TEMP_DIR, DATA_DIR

from pathlib import Path

RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
Path(".files").mkdir(parents=True, exist_ok=True)

@cl.on_chat_start
async def start():
    """Khởi tạo session chat."""
    # Đảm bảo thư mục tồn tại
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    Path(".files").mkdir(parents=True, exist_ok=True)
    
    session_id = cl.user_session.get("id")
    session_tmp_dir = TEMP_DIR / session_id
    session_tmp_dir.mkdir(parents=True, exist_ok=True)
    
    cl.user_session.set("tmp_dir", str(session_tmp_dir))
    
    await cl.Message(
        content="**Chào mừng bạn đến với Lumo Finance AI Assist!**\n\nTôi có thể giúp bạn:\n1. **Tra cứu**: Thông tin từ các báo cáo đã nạp.\n2. **Phân tích**: So sánh chỉ số, vẽ biểu đồ tăng trưởng."
    ).send()

    # [AUTOMATION MODE] AskFileMessage temporarily disabled for screenshot capture
    files = None
    # Sử dụng định dạng dict cho accept để tránh lỗi MIME type
    # try:
    #     files = await cl.AskFileMessage(
    #         content="**Bạn có muốn nạp thêm báo cáo PDF mới không?** (Nhấn cancel để bỏ qua)",
    #         accept={
    #             "application/pdf": [".pdf"]
    #         },
    #         max_size_mb=20,
    #         max_files=5
    #     ).send()
    # except Exception as e:
    #     print(f"AskFileMessage Error: {e}")
    #     return

    if files:
        for file in files:
            safe_filename = os.path.basename(file.name)
            msg = cl.Message(content=f"Đang tiếp nhận file: `{safe_filename}`...")
            await msg.send()
            
            try:
                save_path = RAW_DATA_DIR / safe_filename
                if getattr(file, "path", None):
                    shutil.copy(file.path, save_path)
                elif getattr(file, "content", None) is not None:
                    with open(save_path, "wb") as f:
                        f.write(file.content)
                else:
                    raise ValueError("Không tìm thấy đường dẫn hoặc nội dung tệp tin.")
                
                async with cl.Step(name="Phân tích & Nạp VectorDB") as step:
                    step.output = f"Đang bóc tách văn bản và tạo index cho `{safe_filename}`..."
                    await cl.make_async(ingest_pdf)(str(save_path))
                
                await cl.Message(content=f"Đã nạp thành công `{safe_filename}`!").send()
            except Exception as e:
                await cl.ErrorMessage(content=f"Lỗi nạp file `{safe_filename}`: {str(e)}").send()

@cl.on_message
async def main(message: cl.Message):
    """Xử lý tin nhắn từ người dùng."""
    session_tmp_dir = cl.user_session.get("tmp_dir")
    
    # 1. Kiểm tra nếu có file đính kèm trong tin nhắn
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File) and element.mime == "application/pdf":
                safe_name = os.path.basename(element.name)
                await cl.Message(content=f"Phát hiện file đính kèm: `{safe_name}`. Đang tiến hành nạp...").send()
                try:
                    save_path = RAW_DATA_DIR / safe_name
                    if getattr(element, "path", None):
                        shutil.copy(element.path, save_path)
                    elif getattr(element, "content", None) is not None:
                        with open(save_path, "wb") as f:
                            f.write(element.content)
                    else:
                        raise ValueError("Không tìm thấy đường dẫn hoặc nội dung tệp đính kèm.")
                    await cl.make_async(ingest_pdf)(str(save_path))
                    await cl.Message(content=f"Đã nạp xong `{safe_name}`.").send()
                except Exception as e:
                    await cl.ErrorMessage(content=f"Lỗi nạp `{safe_name}`: {str(e)}").send()

    # 2. Xử lý logic Agent
    thread_id = cl.user_session.get("id")
    
    # Lấy user_id từ database dựa trên email mặc định (longma1@gmail.com)
    user_id = None
    try:
        from core.database import get_db_connection
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE email = %s", ("longma1@gmail.com",))
                row = cur.fetchone()
                if row:
                    user_id = str(row[0])
    except Exception as db_err:
        print(f"[Chainlit] Error loading user_id: {db_err}")
    
    config = {
        "configurable": {
            "session_tmp_dir": session_tmp_dir,
            "thread_id": thread_id,
            "user_id": user_id
        }, 
        "recursion_limit": 25
    }
    
    msg = cl.Message(content="")
    await msg.send()
    
    inputs = {"messages": [HumanMessage(content=message.content)], "steps": []}
    
    try:
        final_state = None
        # Chạy astream với config chứa thread_id để kích hoạt persistence
        async for output in graph_app.astream(inputs, config=config):
            for node, values in output.items():
                async with cl.Step(name=f"Agent: {node.capitalize()}") as step:
                    output_content = ""
                    if "steps" in values and values["steps"]:
                        output_content = values["steps"][-1]
                    else:
                        output_content = f"Đang thực thi {node}..."
                    
                    # Nếu là node Coder, hiển thị thêm code và lỗi nếu có
                    if node == "coder":
                        current_code = values.get("current_code", "")
                        exec_res = values.get("execution_result", "")
                        
                        if current_code:
                            output_content += f"\n\n**Raw Code Execution:**\n```python\n{current_code}\n```"
                        
                        # Hiển thị lỗi nếu có traceback
                        tracebacks = values.get("tracebacks", [])
                        if tracebacks:
                            output_content += f"\n\n**Compiler Error Log (Self-Healing Triggered):**\n```\n{tracebacks[-1]}\n```"
                        elif exec_res and any(x in exec_res for x in ["Traceback", "Error:", "Exception:"]):
                            output_content += f"\n\n**Compiler Error Log (Self-Healing Triggered):**\n```\n{exec_res}\n```"
                    
                    step.output = output_content
                final_state = values

        if final_state and "final_answer" in final_state:
            msg.content = final_state["final_answer"]
            await msg.update()
            
            chart_path = os.path.join(session_tmp_dir, "chart.png")
            if os.path.exists(chart_path):
                image = cl.Image(path=chart_path, name="chart", display="inline")
                await cl.Message(content="**Biểu đồ phân tích:**", elements=[image]).send()
        else:
            await cl.ErrorMessage(content="Agent không thể đưa ra câu trả lời. Vui lòng kiểm tra lại câu hỏi hoặc dữ liệu nguồn.").send()
            
    except Exception as e:
        error_msg = f"**Lỗi hệ thống**: {str(e)}"
        if "Ollama" in str(e):
            error_msg = "**Lỗi kết nối Local LLM**: Vui lòng đảm bảo Ollama đang chạy tại port 11434."
        elif "OpenAI" in str(e):
            error_msg = "**Lỗi API OpenAI**: Vui lòng kiểm tra lại API Key hoặc hạn mức sử dụng."
        
        await cl.ErrorMessage(content=error_msg).send()
        await msg.remove()

@cl.on_chat_end
async def end():
    """Dọn dẹp session khi kết thúc."""
    session_tmp_dir = cl.user_session.get("tmp_dir")
    if session_tmp_dir and os.path.exists(session_tmp_dir):
        try:
            shutil.rmtree(session_tmp_dir)
            print(f"[Cleanup] Đã dọn dẹp thư mục tạm: {session_tmp_dir}")
        except Exception as e:
            print(f"[Cleanup Error] Không thể dọn dẹp: {str(e)}")
