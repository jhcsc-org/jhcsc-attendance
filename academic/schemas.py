from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class SchoolYearBase(BaseModel):
    year_name: str = Field(..., min_length=1, max_length=50)
    start_date: date
    end_date: date

    @field_validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class SchoolYearCreate(SchoolYearBase):
    pass

class SchoolYearUpdate(BaseModel):
    year_name: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SchoolYearResponse(SchoolYearBase):
    id: int

    class Config:
        from_attributes = True

class SemesterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    school_year_id: int = Field(..., gt=0)
    start_date: date
    end_date: date

    @field_validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class SemesterCreate(SemesterBase):
    pass

class SemesterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SemesterResponse(SemesterBase):
    id: int

    class Config:
        from_attributes = True

class SemesterDetailResponse(SemesterResponse):
    school_year: SchoolYearResponse 