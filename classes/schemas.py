from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class ScheduleBase(BaseModel):
    details: str = Field(..., min_length=1)

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleResponse(ScheduleBase):
    id: int

    class Config:
        from_attributes = True

class ClassBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    program_id: int = Field(..., gt=0)
    schedule_id: int = Field(..., gt=0)
    semester_id: int = Field(..., gt=0)

class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    program_id: Optional[int] = Field(None, gt=0)
    schedule_id: Optional[int] = Field(None, gt=0)
    semester_id: Optional[int] = Field(None, gt=0)

class ClassResponse(ClassBase):
    id: int
    schedule: ScheduleResponse

    class Config:
        from_attributes = True

class ClassDetailResponse(ClassResponse):
    teacher_ids: List[int] = []
    student_ids: List[int] = []

class TeacherBase(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=30)

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(TeacherBase):
    name: str | None = Field(None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)

class Teacher(TeacherBase):
    id: int

    class Config:
        from_attributes = True 