from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

from app.schemas.uploads import Upload as UploadSchema

# File attachment schema
class FileAttachment(BaseModel):
    filename: str = Field(..., description="Attachment filename")
    file_path: str = Field(..., description="Path to the file on server")
    file_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., description="Size of the file in bytes")
    file_url: str = Field(..., description="URL to access the file")
    upload_id: int = Field(..., description="关联的上传文件ID")

# Message schemas
class MessageBase(BaseModel):
    role: str = Field(..., description="消息角色，user或assistant")
    content: str = Field(..., description="消息内容")
    attachments: Optional[List[FileAttachment]] = Field(default=None, description="File attachments for the message")

class MessageCreate(MessageBase):
    """创建新消息的请求模型"""
    use_local_model: Optional[bool] = True
    model_name: Optional[str] = "gemma3:27"
    processingTime: Optional[float] = Field(None, description="处理时间（秒）")

class Message(MessageBase):
    id: int
    conversation_id: int
    timestamp: datetime
    processing_time: Optional[float] = None
    use_local_model: Optional[bool] = True
    model_name: Optional[str] = "gemma3:27"
    
    class Config:
        from_attributes = True

# Conversation schemas
class ConversationBase(BaseModel):
    title: str = Field(..., description="对话标题")

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ConversationWithMessages(Conversation):
    messages: List[Message] = []
    
    class Config:
        from_attributes = True

class ConversationList(BaseModel):
    conversations: list[Conversation]
    
    class Config:
        from_attributes = True

class ConversationDetail(Conversation):
    messages: list[Message] = []
    
    class Config:
        from_attributes = True 