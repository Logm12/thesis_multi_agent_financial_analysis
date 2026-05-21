import os
import sys
import shutil
import re
import chainlit as cl
from langchain_core.messages import HumanMessage

# Thêm thư mục src vào path để import các module local
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.graph import app as graph_app, ingest_pdf
from config import TEMP_DIR, DATA_DIR

RAW_DATA_DIR = DATA_DIR / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

@cl.on_chat_start
async def start():
    """Khởi tạo session chat."""
    # Đảm bảo thư mục tồn tại
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    session_id = cl.user_session.get("id")
    session_tmp_dir = TEMP_DIR / session_id
    session_tmp_dir.mkdir(parents=True, exist_ok=True)
    
    cl.user_session.set("tmp_dir", str(session_tmp_dir))
    
    await cl.Message(
        content="🏆 **Chào mừng bạn đến với VNU-IS Financial AI!**\n\nTôi có thể giúp bạn:\n1. 📊 **Tra cứu**: Thông tin từ các báo cáo đã nạp.\n2. 📈 **Phân tích**: So sánh chỉ số, vẽ biểu đồ tăng trưởng."
    ).send()

    # Sử dụng định dạng dict cho accept để tránh lỗi MIME type
    try:
        files = await cl.AskFileMessage(
            content="📁 **Bạn có muốn nạp thêm báo cáo PDF mới không?** (Nhấn cancel để bỏ qua)",
            accept={
                "application/pdf": [".pdf"]
            },
            max_size_mb=20,
            max_files=5
        ).send()
    except Exception as e:
        print(f"AskFileMessage Error: {e}")
        return

    if files:
        for file in files:
            safe_filename = os.path.basename(file.name)
            msg = cl.Message(content=f"📥 Đang tiếp nhận file: `{safe_filename}`...")
            await msg.send()
            
            try:
                save_path = RAW_DATA_DIR / safe_filename
                with open(save_path, "wb") as f:
                    f.write(file.content)
                
                async with cl.Step(name="Phân tích & Nạp VectorDB") as step:
                    step.output = f"Đang bóc tách văn bản và tạo index cho `{safe_filename}`..."
                    await cl.make_async(ingest_pdf)(str(save_path))
                
                await cl.Message(content=f"✅ Đã nạp thành công `{safe_filename}`!").send()
            except Exception as e:
                await cl.ErrorMessage(content=f"❌ Lỗi nạp file `{safe_filename}`: {str(e)}").send()

@cl.on_message
async def main(message: cl.Message):
    """Xử lý tin nhắn từ người dùng."""
    session_tmp_dir = cl.user_session.get("tmp_dir")
    
    # 1. Kiểm tra nếu có file đính kèm trong tin nhắn
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File) and element.mime == "application/pdf":
                safe_name = os.path.basename(element.name)
                await cl.Message(content=f"📑 Phát hiện file đính kèm: `{safe_name}`. Đang tiến hành nạp...").send()
                try:
                    save_path = RAW_DATA_DIR / safe_name
                    with open(save_path, "wb") as f:
                        f.write(element.content)
                    await cl.make_async(ingest_pdf)(str(save_path))
                    await cl.Message(content=f"✅ Đã nạp xong `{safe_name}`.").send()
                except Exception as e:
                    await cl.ErrorMessage(content=f"❌ Lỗi nạp `{safe_name}`: {str(e)}").send()

    # 2. Xử lý logic Agent
    thread_id = cl.user_session.get("id")
    
    config = {
        "configurable": {
            "session_tmp_dir": session_tmp_dir,
            "thread_id": thread_id
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
                    if "steps" in values and values["steps"]:
                        step.output = values["steps"][-1]
                    else:
                        step.output = f"Đang thực thi {node}..."
                final_state = values

        if final_state and "final_answer" in final_state:
            msg.content = final_state["final_answer"]
            await msg.update()
            
            chart_path = os.path.join(session_tmp_dir, "chart.png")
            if os.path.exists(chart_path):
                image = cl.Image(path=chart_path, name="chart", display="inline")
                await cl.Message(content="📊 **Biểu đồ phân tích:**", elements=[image]).send()
        else:
            await cl.ErrorMessage(content="⚠️ Agent không thể đưa ra câu trả lời. Vui lòng kiểm tra lại câu hỏi hoặc dữ liệu nguồn.").send()
            
    except Exception as e:
        error_msg = f"🔥 **Lỗi hệ thống**: {str(e)}"
        if "Ollama" in str(e):
            error_msg = "🔌 **Lỗi kết nối Local LLM**: Vui lòng đảm bảo Ollama đang chạy tại port 11434."
        elif "OpenAI" in str(e):
            error_msg = "🔑 **Lỗi API OpenAI**: Vui lòng kiểm tra lại API Key hoặc hạn mức sử dụng."
        
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
