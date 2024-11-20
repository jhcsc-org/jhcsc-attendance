from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models import SchoolYear, Semester
from academic.schemas import (
    SchoolYearCreate,
    SchoolYearUpdate,
    SemesterCreate,
    SemesterUpdate
)

def get_school_year(db: Session, year_id: int) -> Optional[SchoolYear]:
    """Get a school year by ID"""
    return db.query(SchoolYear).filter(SchoolYear.id == year_id).first()

def get_school_years(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[SchoolYear]:
    """Get all school years"""
    return db.query(SchoolYear).offset(skip).limit(limit).all()

def create_school_year(db: Session, school_year: SchoolYearCreate) -> SchoolYear:
    """Create a new school year"""
    db_school_year = SchoolYear(**school_year.model_dump())
    db.add(db_school_year)
    db.commit()
    db.refresh(db_school_year)
    return db_school_year

def update_school_year(
    db: Session,
    year_id: int,
    school_year: SchoolYearUpdate
) -> SchoolYear:
    """Update a school year"""
    db_school_year = get_school_year(db, year_id)
    if not db_school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School year not found"
        )

    update_data = school_year.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_school_year, field, value)

    db.commit()
    db.refresh(db_school_year)
    return db_school_year

def delete_school_year(db: Session, year_id: int) -> bool:
    """Delete a school year"""
    db_school_year = get_school_year(db, year_id)
    if not db_school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School year not found"
        )

    db.delete(db_school_year)
    db.commit()
    return True

def get_semester(db: Session, semester_id: int) -> Optional[Semester]:
    """Get a semester by ID"""
    return db.query(Semester).filter(Semester.id == semester_id).first()

def get_semesters(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    school_year_id: Optional[int] = None
) -> List[Semester]:
    """Get all semesters with optional school year filtering"""
    query = db.query(Semester)
    if school_year_id:
        query = query.filter(Semester.school_year_id == school_year_id)
    return query.offset(skip).limit(limit).all()

def create_semester(db: Session, semester: SemesterCreate) -> Semester:
    """Create a new semester"""
    # Verify school year exists
    school_year = get_school_year(db, semester.school_year_id)
    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School year not found"
        )

    # Verify semester dates are within school year
    if semester.start_date < school_year.start_date or semester.end_date > school_year.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Semester dates must be within school year dates"
        )

    db_semester = Semester(**semester.model_dump())
    db.add(db_semester)
    db.commit()
    db.refresh(db_semester)
    return db_semester

def update_semester(
    db: Session,
    semester_id: int,
    semester: SemesterUpdate
) -> Semester:
    """Update a semester"""
    db_semester = get_semester(db, semester_id)
    if not db_semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found"
        )

    update_data = semester.model_dump(exclude_unset=True)
    
    # If updating dates, verify they're within school year
    if "start_date" in update_data or "end_date" in update_data:
        school_year = get_school_year(db, db_semester.school_year_id)
        new_start = update_data.get("start_date", db_semester.start_date)
        new_end = update_data.get("end_date", db_semester.end_date)
        
        if new_start < school_year.start_date or new_end > school_year.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Semester dates must be within school year dates"
            )

    for field, value in update_data.items():
        setattr(db_semester, field, value)

    db.commit()
    db.refresh(db_semester)
    return db_semester

def delete_semester(db: Session, semester_id: int) -> bool:
    """Delete a semester"""
    db_semester = get_semester(db, semester_id)
    if not db_semester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semester not found"
        )

    db.delete(db_semester)
    db.commit()
    return True 