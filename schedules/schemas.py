from datetime import time, date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class TimeSlot(BaseModel):
    start_time: time
    end_time: time

    @field_validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class RoomBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    capacity: int = Field(..., gt=0)
    building: str = Field(..., min_length=1, max_length=100)
    floor: int = Field(..., ge=0)

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(None, gt=0)
    building: Optional[str] = Field(None, min_length=1, max_length=100)
    floor: Optional[int] = Field(None, ge=0)

class RoomResponse(RoomBase):
    id: int

    class Config:
        from_attributes = True

class ClassScheduleBase(BaseModel):
    class_id: int = Field(..., gt=0)
    room_id: int = Field(..., gt=0)
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    effective_from: date
    effective_until: date

    @field_validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    @field_validator('effective_until')
    def effective_until_must_be_after_from(cls, v, values):
        if 'effective_from' in values and v < values['effective_from']:
            raise ValueError('effective_until must be after effective_from')
        return v

class ClassScheduleCreate(ClassScheduleBase):
    pass

class ClassScheduleUpdate(BaseModel):
    room_id: Optional[int] = Field(None, gt=0)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    effective_until: Optional[date] = None

class ClassScheduleResponse(ClassScheduleBase):
    id: int
    room: RoomResponse

    class Config:
        from_attributes = True

class ScheduleConflict(BaseModel):
    conflict_type: str
    message: str
    conflicting_schedule_id: int 