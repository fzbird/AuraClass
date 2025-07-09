from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

# 共享属性
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True

# 创建时的额外属性
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_id: int
    class_id: Optional[int] = None

# 更新时的属性
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8)
    role_id: Optional[int] = None
    class_id: Optional[int] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True

# 数据库中查询的响应
class UserInDB(UserBase):
    id: int
    role_id: int
    class_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# API 响应
class User(UserInDB):
    pass

# 用户列表响应
class UserListResponse(BaseModel):
    data: List[User]
    meta: dict

    class Config:
        from_attributes = True
