from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from profiles import service
from profiles.schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])

@router.get("", response_model=List[StudentResponse])
def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(active|inactive|suspended|graduated)$"),
    db: AsyncSession = Depends(get_db)
) -> List[StudentResponse]:
    """
    Retrieve a list of students with optional filtering by status.
    """
    return service.get_students(db, skip, limit, status)

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> StudentResponse:
    """
    Retrieve a specific student by ID.
    """
    student = service.get_student_by_id(db, student_id)
    return student

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_db)
) -> StudentResponse:
    """
    Create a new student.
    """
    return service.create_student(db, student)

@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: AsyncSession = Depends(get_db)
) -> StudentResponse:
    """
    Update a student's information.
    """
    return service.update_student(db, student_id, student_update)

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a student.
    """
    service.delete_student(db, student_id) 