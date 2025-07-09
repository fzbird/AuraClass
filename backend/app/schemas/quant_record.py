from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, validator

class QuantRecordBase(BaseModel):
    student_id: int = Field(..., gt=0, description="学生ID")
    item_id: int = Field(..., gt=0, description="量化项目ID")
    score: Decimal = Field(..., ge=-100, le=100, description="分数，范围：-100到100")
    reason: str = Field(..., min_length=1, max_length=500, description="原因说明")
    record_date: date = Field(..., description="记录日期")

class QuantRecordCreate(QuantRecordBase):
    recorder_id: int

class QuantRecordBatchCreate(BaseModel):
    records: List[QuantRecordCreate]

class QuantRecordUpdate(BaseModel):
    score: Optional[Decimal] = Field(None, ge=-100, le=100, description="分数，范围：-100到100")
    reason: Optional[str] = None
    record_date: Optional[date] = None
    
    class Config:
        from_attributes = True

class QuantRecordInDB(QuantRecordBase):
    id: int
    recorder_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class QuantRecord(QuantRecordInDB):
    # 可以添加关联数据
    student_name: Optional[str] = None
    item_name: Optional[str] = None
    recorder_name: Optional[str] = None
    reason: Optional[str] = None  # 允许为空
    
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True

# 保留此类以保持向后兼容性，但不再在主API中使用
class QuantRecordListResponse(BaseModel):
    data: List[QuantRecord]
    meta: dict
    
    class Config:
        from_attributes = True
