from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    grade: str = Field(..., min_length=1, max_length=20)
    year: int = Field(..., gt=2000, lt=2100)
    head_teacher_id: Optional[int] = None

class ClassCreate(ClassBase):
    @field_validator('head_teacher_id')
    @classmethod
    def validate_head_teacher_id(cls, v: Optional[int]) -> Optional[int]:
        if v == 0:
            return None
        if v is not None and v < 1:
            raise ValueError("班主任ID必须大于0")
        return v

class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    grade: Optional[str] = Field(None, min_length=1, max_length=20)
    year: Optional[int] = Field(None, gt=2000, lt=2100)
    head_teacher_id: Optional[int] = None
    
    @field_validator('head_teacher_id')
    @classmethod
    def validate_head_teacher_id(cls, v: Optional[int]) -> Optional[int]:
        if v == 0:
            return None
        if v is not None and v < 1:
            raise ValueError("班主任ID必须大于0")
        return v
    
    class Config:
        from_attributes = True

class Classes(ClassBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ClassListResponse(BaseModel):
    data: List[Classes]
    meta: dict
    
    class Config:
        from_attributes = True
