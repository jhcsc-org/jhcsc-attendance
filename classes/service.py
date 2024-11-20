from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import Class, Schedule, ClassTeachers, ClassStudents
from classes.schemas import ClassCreate, ClassUpdate, ScheduleCreate

def get_class(db: Session, class_id: int) -> Optional[Class]:
    """Get a class by ID"""
    return db.query(Class).filter(Class.id == class_id).first()

def get_classes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    program_id: Optional[int] = None
) -> List[Class]:
    """Get all classes with optional program filtering"""
    query = db.query(Class)
    if program_id:
        query = query.filter(Class.program_id == program_id)
    return query.offset(skip).limit(limit).all()

def create_class(db: Session, class_data: ClassCreate) -> Class:
    """Create a new class"""
    # Verify schedule exists
    schedule = db.query(Schedule).filter(Schedule.id == class_data.schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    db_class = Class(**class_data.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def update_class(
    db: Session,
    class_id: int,
    class_update: ClassUpdate
) -> Class:
    """Update a class"""
    db_class = get_class(db, class_id)
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    update_data = class_update.model_dump(exclude_unset=True)
    
    # If updating schedule, verify it exists
    if "schedule_id" in update_data:
        schedule = db.query(Schedule).filter(Schedule.id == update_data["schedule_id"]).first()
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )

    for field, value in update_data.items():
        setattr(db_class, field, value)

    db.commit()
    db.refresh(db_class)
    return db_class

def delete_class(db: Session, class_id: int) -> bool:
    """Delete a class"""
    db_class = get_class(db, class_id)
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    db.delete(db_class)
    db.commit()
    return True

def add_student_to_class(db: Session, class_id: int, student_id: int) -> bool:
    """Add a student to a class"""
    # Check if class exists
    db_class = get_class(db, class_id)
    if not db_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    # Check if student is already in class
    existing = db.query(ClassStudents).filter(
        ClassStudents.class_id == class_id,
        ClassStudents.student_id == student_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already in class"
        )

    class_student = ClassStudents(class_id=class_id, student_id=student_id)
    db.add(class_student)
    db.commit()
    return True

def remove_student_from_class(db: Session, class_id: int, student_id: int) -> bool:
    """Remove a student from a class"""
    result = db.query(ClassStudents).filter(
        ClassStudents.class_id == class_id,
        ClassStudents.student_id == student_id
    ).delete()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found in class"
        )
    
    db.commit()
    return True 