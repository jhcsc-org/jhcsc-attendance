from typing import List, Optional
from pydantic import BaseModel, Field

class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class ProgramBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    department_id: int = Field(..., gt=0)

class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    department_id: Optional[int] = Field(None, gt=0)

class ProgramResponse(ProgramBase):
    id: int

    class Config:
        from_attributes = True

class DepartmentResponse(DepartmentBase):
    id: int
    programs: List[ProgramResponse] = []

    class Config:
        from_attributes = True 