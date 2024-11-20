from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, field_validator

from models import AttendanceMethod, AttendanceStatus

class AttendanceSessionBase(BaseModel):
    class_id: int = Field(..., gt=0)
    method: AttendanceMethod
    start_time: datetime
    end_time: Optional[datetime] = None
    settings: Dict = Field(default_factory=dict)

class AttendanceSessionCreate(AttendanceSessionBase):
    pass

class AttendanceSessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    is_finalized: Optional[bool] = None
    settings: Optional[Dict] = None

    @field_validator('end_time')
    def end_time_must_be_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('end_time must be in the future')
        return v

class AttendanceRecordBase(BaseModel):
    student_id: int = Field(..., gt=0)
    status: AttendanceStatus
    verification_method: str
    verification_data: Optional[Dict] = None
    notes: Optional[str] = None

class AttendanceRecordCreate(AttendanceRecordBase):
    pass

class AttendanceRecordUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None

class AttendanceAdjustmentCreate(BaseModel):
    record_id: int = Field(..., gt=0)
    new_status: AttendanceStatus
    reason: str = Field(..., min_length=1)

class AttendanceVerificationCreate(BaseModel):
    method: str = Field(..., min_length=1)
    data: Dict = Field(...)

class AttendanceSessionResponse(AttendanceSessionBase):
    id: int
    teacher_id: int
    is_finalized: bool
    qr_code: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AttendanceRecordResponse(AttendanceRecordBase):
    id: int
    session_id: int
    recorded_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AttendanceAdjustmentResponse(BaseModel):
    id: int
    record_id: int
    adjusted_by_id: int
    previous_status: AttendanceStatus
    new_status: AttendanceStatus
    reason: str
    adjusted_at: datetime

    class Config:
        from_attributes = True

class AttendanceSessionDetail(AttendanceSessionResponse):
    records: List[AttendanceRecordResponse]
    adjustments: List[AttendanceAdjustmentResponse]

class AttendanceStats(BaseModel):
    total_students: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_rate: float 