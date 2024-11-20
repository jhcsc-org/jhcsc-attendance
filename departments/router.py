from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from departments import service
from departments.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse
)

router = APIRouter(tags=["departments"])

# Department routes
@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[DepartmentResponse]:
    """
    Retrieve a list of departments.
    """
    return service.get_departments(db, skip, limit)

@router.get("/departments/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db)
) -> DepartmentResponse:
    """
    Retrieve a specific department by ID.
    """
    return service.get_department(db, department_id)

@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db)
) -> DepartmentResponse:
    """
    Create a new department.
    """
    return service.create_department(db, department)

@router.patch("/departments/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    department: DepartmentUpdate,
    db: Session = Depends(get_db)
) -> DepartmentResponse:
    """
    Update a department's information.
    """
    return service.update_department(db, department_id, department)

@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a department.
    """
    service.delete_department(db, department_id)

# Program routes
@router.get("/programs", response_model=List[ProgramResponse])
def get_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    department_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
) -> List[ProgramResponse]:
    """
    Retrieve a list of programs with optional department filtering.
    """
    return service.get_programs(db, skip, limit, department_id)

@router.get("/programs/{program_id}", response_model=ProgramResponse)
def get_program(
    program_id: int,
    db: Session = Depends(get_db)
) -> ProgramResponse:
    """
    Retrieve a specific program by ID.
    """
    return service.get_program(db, program_id)

@router.post("/programs", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program: ProgramCreate,
    db: Session = Depends(get_db)
) -> ProgramResponse:
    """
    Create a new program.
    """
    return service.create_program(db, program)

@router.patch("/programs/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: int,
    program: ProgramUpdate,
    db: Session = Depends(get_db)
) -> ProgramResponse:
    """
    Update a program's information.
    """
    return service.update_program(db, program_id, program)

@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a program.
    """
    service.delete_program(db, program_id) 