from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from teachers import service
from teachers.schemas import (
    TeacherCreate,
    TeacherUpdate,
    TeacherResponse,
    TeacherClassAssignment
)

router = APIRouter(prefix="/teachers", tags=["teachers"])

@router.get("", response_model=List[TeacherResponse])
def get_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[TeacherResponse]:
    """
    Retrieve a list of teachers.
    """
    return service.get_teachers(db, skip, limit)

@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db)
) -> TeacherResponse:
    """
    Retrieve a specific teacher by ID.
    """
    return service.get_teacher(db, teacher_id)

@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher: TeacherCreate,
    db: Session = Depends(get_db)
) -> TeacherResponse:
    """
    Create a new teacher.
    """
    return service.create_teacher(db, teacher)

@router.patch("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher: TeacherUpdate,
    db: Session = Depends(get_db)
) -> TeacherResponse:
    """
    Update a teacher's information.
    """
    return service.update_teacher(db, teacher_id, teacher)

@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a teacher.
    """
    service.delete_teacher(db, teacher_id)

@router.post("/{teacher_id}/classes")
def assign_to_class(
    teacher_id: int,
    assignment: TeacherClassAssignment,
    db: Session = Depends(get_db)
) -> dict:
    """
    Assign a teacher to a class.
    """
    service.assign_class(db, teacher_id, assignment.class_id)
    return {"message": "Teacher assigned to class successfully"}

@router.delete("/{teacher_id}/classes/{class_id}")
def remove_from_class(
    teacher_id: int,
    class_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Remove a teacher's assignment from a class.
    """
    service.remove_class_assignment(db, teacher_id, class_id)
    return {"message": "Teacher removed from class successfully"} 