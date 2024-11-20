from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import Department, Program
from departments.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    ProgramCreate,
    ProgramUpdate
)

def get_department(db: Session, department_id: int) -> Optional[Department]:
    """Get a department by ID"""
    return db.query(Department).filter(Department.id == department_id).first()

def get_departments(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Department]:
    """Get all departments"""
    return db.query(Department).offset(skip).limit(limit).all()

def create_department(db: Session, department: DepartmentCreate) -> Department:
    """Create a new department"""
    db_department = Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def update_department(
    db: Session,
    department_id: int,
    department: DepartmentUpdate
) -> Department:
    """Update a department"""
    db_department = get_department(db, department_id)
    if not db_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    update_data = department.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_department, field, value)

    db.commit()
    db.refresh(db_department)
    return db_department

def delete_department(db: Session, department_id: int) -> bool:
    """Delete a department"""
    db_department = get_department(db, department_id)
    if not db_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    if db_department.programs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete department with existing programs"
        )

    db.delete(db_department)
    db.commit()
    return True

def get_program(db: Session, program_id: int) -> Optional[Program]:
    """Get a program by ID"""
    return db.query(Program).filter(Program.id == program_id).first()

def get_programs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None
) -> List[Program]:
    """Get all programs with optional department filtering"""
    query = db.query(Program)
    if department_id:
        query = query.filter(Program.department_id == department_id)
    return query.offset(skip).limit(limit).all()

def create_program(db: Session, program: ProgramCreate) -> Program:
    """Create a new program"""
    # Verify department exists
    department = get_department(db, program.department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    db_program = Program(**program.model_dump())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

def update_program(
    db: Session,
    program_id: int,
    program: ProgramUpdate
) -> Program:
    """Update a program"""
    db_program = get_program(db, program_id)
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )

    update_data = program.model_dump(exclude_unset=True)
    
    # If updating department, verify it exists
    if "department_id" in update_data:
        department = get_department(db, update_data["department_id"])
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )

    for field, value in update_data.items():
        setattr(db_program, field, value)

    db.commit()
    db.refresh(db_program)
    return db_program

def delete_program(db: Session, program_id: int) -> bool:
    """Delete a program"""
    db_program = get_program(db, program_id)
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found"
        )

    if db_program.classes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete program with existing classes"
        )

    db.delete(db_program)
    db.commit()
    return True 