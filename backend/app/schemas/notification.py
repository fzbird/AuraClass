from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator

class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="通知标题")
    content: str = Field(..., min_length=1, description="通知内容")
    notification_type: str = Field(..., pattern="^(system|quant|message|role)$", description="通知类型：system-系统通知，quant-量化通知，message-消息通知，role-角色通知")
    recipient_user_id: Optional[int] = Field(None, ge=1, description="接收者用户ID，如果是发给特定用户则必填，0或不提供表示不指定用户")
    recipient_role_id: Optional[int] = Field(None, ge=1, description="接收者角色ID，如果是发给特定角色则必填，0或不提供表示不指定角色")
    
    @validator('recipient_user_id', 'recipient_role_id', pre=True)
    def validate_ids(cls, v):
        if v == 0:
            return None
        return v

class NotificationCreate(NotificationBase):
    sender_id: int = Field(..., description="发送者ID，通常由系统自动设置为当前用户ID")

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None

class NotificationInDB(NotificationBase):
    id: int
    sender_id: int
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Notification(NotificationInDB):
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None

    class Config:
        from_attributes = True

class NotificationList(BaseModel):
    data: List[Notification]
    meta: dict

    class Config:
        from_attributes = True
