from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class TeacherBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)

class TeacherResponse(TeacherBase):
    id: int
    class_ids: List[int] = []

    class Config:
        from_attributes = True

class TeacherClassAssignment(BaseModel):
    class_id: int = Field(..., gt=0) 