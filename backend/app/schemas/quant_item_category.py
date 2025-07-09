from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

class QuantItemCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="分类名称")
    description: Optional[str] = None
    order: int = Field(0, ge=0, description="排序顺序，值越小越靠前")
    is_active: bool = True

class QuantItemCategoryCreate(QuantItemCategoryBase):
    pass

class QuantItemCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

class QuantItemCategory(QuantItemCategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuantItemCategoryListResponse(BaseModel):
    data: List[QuantItemCategory]
    meta: dict
    
    class Config:
        from_attributes = True 