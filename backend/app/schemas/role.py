from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    
    class Config:
        from_attributes = True

class Role(RoleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoleListResponse(BaseModel):
    data: List[Role]
    meta: dict
    
    class Config:
        from_attributes = True
