from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schedules import service
from schedules.schemas import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    ClassScheduleCreate,
    ClassScheduleUpdate,
    ClassScheduleResponse
)

router = APIRouter(tags=["schedules"])

@router.get("/rooms", response_model=List[RoomResponse])
def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    building: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[RoomResponse]:
    """
    Retrieve a list of rooms with optional building filter.
    """
    return service.get_rooms(db, skip, limit, building)

@router.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room(
    room_id: int,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Retrieve a specific room by ID.
    """
    return service.get_room(db, room_id)

@router.post("/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(
    room: RoomCreate,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Create a new room.
    """
    return service.create_room(db, room)

@router.patch("/rooms/{room_id}", response_model=RoomResponse)
def update_room(
    room_id: int,
    room: RoomUpdate,
    db: Session = Depends(get_db)
) -> RoomResponse:
    """
    Update a room's information.
    """
    return service.update_room(db, room_id, room)

@router.delete("/rooms/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a room.
    """
    service.delete_room(db, room_id)

# Class Schedule routes
@router.get("/schedules", response_model=List[ClassScheduleResponse])
def get_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    class_id: Optional[int] = Query(None, gt=0),
    room_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
) -> List[ClassScheduleResponse]:
    """
    Retrieve a list of class schedules with optional filters.
    """
    return service.get_class_schedules(db, class_id, room_id, skip, limit)

@router.get("/schedules/{schedule_id}", response_model=ClassScheduleResponse)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
) -> ClassScheduleResponse:
    """
    Retrieve a specific class schedule by ID.
    """
    return service.get_class_schedule(db, schedule_id)

@router.post("/schedules", response_model=ClassScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_schedule(
    schedule: ClassScheduleCreate,
    db: Session = Depends(get_db)
) -> ClassScheduleResponse:
    """
    Create a new class schedule.
    """
    return service.create_class_schedule(db, schedule)

@router.patch("/schedules/{schedule_id}", response_model=ClassScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule: ClassScheduleUpdate,
    db: Session = Depends(get_db)
) -> ClassScheduleResponse:
    """
    Update a class schedule.
    """
    return service.update_class_schedule(db, schedule_id, schedule)

@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a class schedule.
    """
    service.delete_class_schedule(db, schedule_id) 