from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field

class QuantItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    min_score: Decimal = Field(..., ge=-100, le=100, description="最小分数，范围：-100到100")
    max_score: Decimal = Field(..., ge=-100, le=100, description="最大分数，范围：-100到100")
    default_score: Optional[Decimal] = Field(None, ge=-100, le=100, description="默认分数，范围：-100到100")
    default_reason: Optional[str] = None
    weight: Decimal = Field(1.0, ge=0, le=10, description="权重，范围：0到10")
    category: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[int] = None
    is_active: bool = True

class QuantItemCreate(QuantItemBase):
    pass

class QuantItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    min_score: Optional[Decimal] = Field(None, ge=-100, le=100, description="最小分数，范围：-100到100")
    max_score: Optional[Decimal] = Field(None, ge=-100, le=100, description="最大分数，范围：-100到100")
    default_score: Optional[Decimal] = Field(None, ge=-100, le=100, description="默认分数，范围：-100到100")
    default_reason: Optional[str] = None
    weight: Optional[Decimal] = Field(None, ge=0, le=10, description="权重，范围：0到10")
    category: Optional[str] = Field(None, min_length=1, max_length=50)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

class QuantItem(QuantItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuantItemListResponse(BaseModel):
    data: List[QuantItem]
    meta: dict
    
    class Config:
        from_attributes = True
