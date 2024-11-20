from typing import List, Optional
from datetime import time, date
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import Room, ClassSchedule, Class
from schedules.schemas import (
    RoomCreate,
    RoomUpdate,
    ClassScheduleCreate,
    ClassScheduleUpdate,
    ScheduleConflict
)

def get_room(db: Session, room_id: int) -> Optional[Room]:
    """Get a room by ID"""
    return db.query(Room).filter(Room.id == room_id).first()

def get_rooms(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    building: Optional[str] = None
) -> List[Room]:
    """Get all rooms with optional building filter"""
    query = db.query(Room)
    if building:
        query = query.filter(Room.building == building)
    return query.offset(skip).limit(limit).all()

def create_room(db: Session, room: RoomCreate) -> Room:
    """Create a new room"""
    db_room = Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def update_room(
    db: Session,
    room_id: int,
    room: RoomUpdate
) -> Room:
    """Update a room"""
    db_room = get_room(db, room_id)
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    update_data = room.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_room, field, value)

    db.commit()
    db.refresh(db_room)
    return db_room

def delete_room(db: Session, room_id: int) -> bool:
    """Delete a room"""
    db_room = get_room(db, room_id)
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    if db_room.schedules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete room with existing schedules"
        )

    db.delete(db_room)
    db.commit()
    return True

def check_schedule_conflicts(
    db: Session,
    room_id: int,
    day_of_week: int,
    start_time: time,
    end_time: time,
    effective_from: date,
    effective_until: date,
    exclude_schedule_id: Optional[int] = None
) -> Optional[ScheduleConflict]:
    """Check for scheduling conflicts"""
    query = db.query(ClassSchedule).filter(
        ClassSchedule.room_id == room_id,
        ClassSchedule.day_of_week == day_of_week,
        or_(
            and_(
                ClassSchedule.start_time <= start_time,
                ClassSchedule.end_time > start_time
            ),
            and_(
                ClassSchedule.start_time < end_time,
                ClassSchedule.end_time >= end_time
            )
        ),
        or_(
            and_(
                ClassSchedule.effective_from <= effective_from,
                ClassSchedule.effective_until > effective_from
            ),
            and_(
                ClassSchedule.effective_from < effective_until,
                ClassSchedule.effective_until >= effective_until
            )
        )
    )

    if exclude_schedule_id:
        query = query.filter(ClassSchedule.id != exclude_schedule_id)

    conflict = query.first()
    if conflict:
        return ScheduleConflict(
            conflict_type="time_overlap",
            message="Schedule conflicts with existing booking",
            conflicting_schedule_id=conflict.id
        )
    return None

def create_class_schedule(
    db: Session,
    schedule: ClassScheduleCreate
) -> ClassSchedule:
    """Create a new class schedule"""
    # Verify class exists
    class_exists = db.query(Class).filter(Class.id == schedule.class_id).first()
    if not class_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    # Verify room exists
    room = get_room(db, schedule.room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    # Check for conflicts
    conflict = check_schedule_conflicts(
        db,
        schedule.room_id,
        schedule.day_of_week,
        schedule.start_time,
        schedule.end_time,
        schedule.effective_from,
        schedule.effective_until
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=conflict.message
        )

    db_schedule = ClassSchedule(**schedule.model_dump())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def get_class_schedule(db: Session, schedule_id: int) -> Optional[ClassSchedule]:
    """Get a class schedule by ID"""
    return db.query(ClassSchedule).filter(ClassSchedule.id == schedule_id).first()

def get_class_schedules(
    db: Session,
    class_id: Optional[int] = None,
    room_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ClassSchedule]:
    """Get class schedules with optional filters"""
    query = db.query(ClassSchedule)
    if class_id:
        query = query.filter(ClassSchedule.class_id == class_id)
    if room_id:
        query = query.filter(ClassSchedule.room_id == room_id)
    return query.offset(skip).limit(limit).all()

def update_class_schedule(
    db: Session,
    schedule_id: int,
    schedule: ClassScheduleUpdate
) -> ClassSchedule:
    """Update a class schedule"""
    db_schedule = get_class_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    update_data = schedule.model_dump(exclude_unset=True)
    
    # If updating room or time, check for conflicts
    if any(field in update_data for field in ['room_id', 'start_time', 'end_time']):
        conflict = check_schedule_conflicts(
            db,
            update_data.get('room_id', db_schedule.room_id),
            db_schedule.day_of_week,
            update_data.get('start_time', db_schedule.start_time),
            update_data.get('end_time', db_schedule.end_time),
            db_schedule.effective_from,
            update_data.get('effective_until', db_schedule.effective_until),
            exclude_schedule_id=schedule_id
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=conflict.message
            )

    for field, value in update_data.items():
        setattr(db_schedule, field, value)

    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def delete_class_schedule(db: Session, schedule_id: int) -> bool:
    """Delete a class schedule"""
    db_schedule = get_class_schedule(db, schedule_id)
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    db.delete(db_schedule)
    db.commit()
    return True 