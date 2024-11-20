from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    gender: str = Field(..., pattern="^(male|female|other)$")
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    status: str = Field(..., pattern="^(active|inactive|suspended|graduated)$")

class StudentCreate(StudentBase):
    student_id: str = Field(..., min_length=1, max_length=50)
    enrollment_date: date

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|suspended|graduated)$")

class StudentResponse(StudentBase):
    id: int
    student_id: str
    enrollment_date: date

    class Config:
        from_attributes = True 