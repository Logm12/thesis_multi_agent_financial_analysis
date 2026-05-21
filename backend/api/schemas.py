from pydantic import BaseModel, Field
from typing import Optional, Any, Literal

class ChatRequest(BaseModel):
    """Schema cho yêu cầu chat."""
    message: str = Field(..., description="Nội dung tin nhắn từ người dùng")
    session_id: str = Field("default", description="ID phiên làm việc để duy trì ngữ cảnh (thread_id)")

class ChatResponse(BaseModel):
    """Schema cho phản hồi chat."""
    status: Literal["success", "error"] = Field(..., description="Trạng thái phản hồi")
    data: Optional[Any] = Field(None, description="Dữ liệu trả về từ Agent")
    message: str = Field("", description="Thông báo đi kèm (thường dùng khi có lỗi)")

class UploadResponse(BaseModel):
    """Schema cho phản hồi upload."""
    task_id: str = Field(..., description="ID của task xử lý ngầm")
    message: str = Field(..., description="Thông báo trạng thái")

class StatusResponse(BaseModel):
    """Schema cho trạng thái task."""
    task_id: str = Field(..., description="ID của task")
    status: str = Field(..., description="Trạng thái: pending, processing, completed, failed")
    details: str = Field(..., description="Chi tiết trạng thái hoặc lỗi")
