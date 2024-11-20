from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from classes import service
from classes.schemas import (
    ClassCreate,
    ClassUpdate,
    ClassResponse,
    ClassDetailResponse
)

router = APIRouter(prefix="/classes", tags=["classes"])

@router.get("", response_model=List[ClassResponse])
def get_classes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    program_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
) -> List[ClassResponse]:
    """
    Retrieve a list of classes with optional program filtering.
    """
    return service.get_classes(db, skip, limit, program_id)

@router.get("/{class_id}", response_model=ClassDetailResponse)
def get_class(
    class_id: int,
    db: Session = Depends(get_db)
) -> ClassDetailResponse:
    """
    Retrieve a specific class by ID.
    """
    return service.get_class(db, class_id)

@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: ClassCreate,
    db: Session = Depends(get_db)
) -> ClassResponse:
    """
    Create a new class.
    """
    return service.create_class(db, class_data)

@router.patch("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_update: ClassUpdate,
    db: Session = Depends(get_db)
) -> ClassResponse:
    """
    Update a class's information.
    """
    return service.update_class(db, class_id, class_update)

@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class(
    class_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a class.
    """
    service.delete_class(db, class_id)

@router.post("/{class_id}/students/{student_id}")
def add_student(
    class_id: int,
    student_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Add a student to a class.
    """
    service.add_student_to_class(db, class_id, student_id)
    return {"message": "Student added to class successfully"}

@router.delete("/{class_id}/students/{student_id}")
def remove_student(
    class_id: int,
    student_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Remove a student from a class.
    """
    service.remove_student_from_class(db, class_id, student_id)
    return {"message": "Student removed from class successfully"} 