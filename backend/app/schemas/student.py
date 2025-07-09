from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

class StudentBase(BaseModel):
    student_id_no: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    class_id: int = Field(..., gt=0, description="班级ID，必须大于0")
    gender: str = Field(..., min_length=1, max_length=10)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    contact_info: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=255)
    is_active: bool = True
    user_id: Optional[int] = None

class StudentCreate(StudentBase):
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: Optional[int]) -> Optional[int]:
        if v == 0:
            return None
        if v is not None and v < 1:
            raise ValueError("用户ID必须大于0")
        return v

class StudentUpdate(BaseModel):
    student_id_no: Optional[str] = Field(None, min_length=1, max_length=50)
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    class_id: Optional[int] = Field(None, gt=0, description="班级ID，必须大于0")
    gender: Optional[str] = Field(None, min_length=1, max_length=10)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    contact_info: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=255)
    total_score: Optional[float] = None
    rank: Optional[int] = None
    is_active: Optional[bool] = None
    user_id: Optional[int] = None
    
    @field_validator('class_id')
    @classmethod
    def validate_class_id(cls, v: Optional[int]) -> Optional[int]:
        if v == 0:
            return None
        if v is not None and v < 1:
            raise ValueError("班级ID必须大于0")
        return v

    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: Optional[int]) -> Optional[int]:
        if v == 0:
            return None
        if v is not None and v < 1:
            raise ValueError("用户ID必须大于0")
        return v
    
    class Config:
        from_attributes = True

class Student(StudentBase):
    id: int
    total_score: Optional[float] = None
    rank: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    data: List[Student]
    meta: dict
    
    class Config:
        from_attributes = True
