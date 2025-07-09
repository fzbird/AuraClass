from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class UploadBase(BaseModel):
    """文件上传基础模型"""
    filename: str = Field(..., description="文件名")
    original_filename: str = Field(..., description="原始文件名")
    file_path: str = Field(..., description="文件相对路径")
    file_type: str = Field(..., description="文件MIME类型")
    file_size: int = Field(..., description="文件大小（字节）")
    module: str = Field(..., description="所属模块")
    entity_type: Optional[str] = Field(None, description="实体类型")
    entity_id: Optional[int] = Field(None, description="关联实体ID")
    is_public: int = Field(0, description="是否公开，0-私有，1-公开")


class UploadCreate(UploadBase):
    """创建文件上传模型"""
    uploader_id: int = Field(..., description="上传者ID")


class UploadUpdate(BaseModel):
    """更新文件上传模型"""
    filename: Optional[str] = None
    file_path: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    is_public: Optional[int] = None


class UploadInDB(UploadBase):
    """数据库中的文件上传模型"""
    id: int
    uploader_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Upload(UploadInDB):
    """文件上传模型，用于API响应"""
    file_url: str = Field(..., description="文件的完整URL路径")

    class Config:
        from_attributes = True


class UploadList(BaseModel):
    """文件上传列表模型"""
    uploads: List[Upload]
    total: int
    page: int
    size: int

    class Config:
        from_attributes = True 