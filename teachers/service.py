from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import Teacher, Class, ClassTeachers
from teachers.schemas import TeacherCreate, TeacherUpdate

def get_teacher(db: Session, teacher_id: int) -> Optional[Teacher]:
    """Get a teacher by ID"""
    return db.query(Teacher).filter(Teacher.id == teacher_id).first()

def get_teacher_by_email(db: Session, email: str) -> Optional[Teacher]:
    """Get a teacher by email"""
    return db.query(Teacher).filter(Teacher.email == email).first()

def get_teachers(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Teacher]:
    """Get all teachers"""
    return db.query(Teacher).offset(skip).limit(limit).all()

def create_teacher(db: Session, teacher: TeacherCreate) -> Teacher:
    """Create a new teacher"""
    # Check if email already exists
    if get_teacher_by_email(db, teacher.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    db_teacher = Teacher(**teacher.model_dump())
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def update_teacher(
    db: Session,
    teacher_id: int,
    teacher: TeacherUpdate
) -> Teacher:
    """Update a teacher"""
    db_teacher = get_teacher(db, teacher_id)
    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    update_data = teacher.model_dump(exclude_unset=True)
    
    # If updating email, check if it's already taken
    if "email" in update_data:
        existing_teacher = get_teacher_by_email(db, update_data["email"])
        if existing_teacher and existing_teacher.id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    for field, value in update_data.items():
        setattr(db_teacher, field, value)

    db.commit()
    db.refresh(db_teacher)
    return db_teacher

def delete_teacher(db: Session, teacher_id: int) -> bool:
    """Delete a teacher"""
    db_teacher = get_teacher(db, teacher_id)
    if not db_teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    if db_teacher.classes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete teacher assigned to classes"
        )

    db.delete(db_teacher)
    db.commit()
    return True

def assign_class(db: Session, teacher_id: int, class_id: int) -> bool:
    """Assign a teacher to a class"""
    # Verify teacher exists
    teacher = get_teacher(db, teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Verify class exists
    class_exists = db.query(Class).filter(Class.id == class_id).first()
    if not class_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    # Check if assignment already exists
    existing = db.query(ClassTeachers).filter(
        ClassTeachers.teacher_id == teacher_id,
        ClassTeachers.class_id == class_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher already assigned to this class"
        )

    class_teacher = ClassTeachers(class_id=class_id, teacher_id=teacher_id)
    db.add(class_teacher)
    db.commit()
    return True

def remove_class_assignment(db: Session, teacher_id: int, class_id: int) -> bool:
    """Remove a teacher's assignment from a class"""
    result = db.query(ClassTeachers).filter(
        ClassTeachers.teacher_id == teacher_id,
        ClassTeachers.class_id == class_id
    ).delete()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not assigned to this class"
        )
    
    db.commit()
    return True 