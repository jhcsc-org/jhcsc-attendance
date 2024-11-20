from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from academic import service
from academic.schemas import (
    SchoolYearCreate,
    SchoolYearUpdate,
    SchoolYearResponse,
    SemesterCreate,
    SemesterUpdate,
    SemesterResponse,
    SemesterDetailResponse
)

router = APIRouter(tags=["academic"])

# School Year routes
@router.get("/school-years", response_model=List[SchoolYearResponse])
def get_school_years(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[SchoolYearResponse]:
    """
    Retrieve a list of school years.
    """
    return service.get_school_years(db, skip, limit)

@router.get("/school-years/{year_id}", response_model=SchoolYearResponse)
def get_school_year(
    year_id: int,
    db: Session = Depends(get_db)
) -> SchoolYearResponse:
    """
    Retrieve a specific school year by ID.
    """
    return service.get_school_year(db, year_id)

@router.post("/school-years", response_model=SchoolYearResponse, status_code=status.HTTP_201_CREATED)
def create_school_year(
    school_year: SchoolYearCreate,
    db: Session = Depends(get_db)
) -> SchoolYearResponse:
    """
    Create a new school year.
    """
    return service.create_school_year(db, school_year)

@router.patch("/school-years/{year_id}", response_model=SchoolYearResponse)
def update_school_year(
    year_id: int,
    school_year: SchoolYearUpdate,
    db: Session = Depends(get_db)
) -> SchoolYearResponse:
    """
    Update a school year's information.
    """
    return service.update_school_year(db, year_id, school_year)

@router.delete("/school-years/{year_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school_year(
    year_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a school year.
    """
    service.delete_school_year(db, year_id)

# Semester routes
@router.get("/semesters", response_model=List[SemesterResponse])
def get_semesters(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    school_year_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
) -> List[SemesterResponse]:
    """
    Retrieve a list of semesters with optional school year filtering.
    """
    return service.get_semesters(db, skip, limit, school_year_id)

@router.get("/semesters/{semester_id}", response_model=SemesterDetailResponse)
def get_semester(
    semester_id: int,
    db: Session = Depends(get_db)
) -> SemesterDetailResponse:
    """
    Retrieve a specific semester by ID.
    """
    return service.get_semester(db, semester_id)

@router.post("/semesters", response_model=SemesterResponse, status_code=status.HTTP_201_CREATED)
def create_semester(
    semester: SemesterCreate,
    db: Session = Depends(get_db)
) -> SemesterResponse:
    """
    Create a new semester.
    """
    return service.create_semester(db, semester)

@router.patch("/semesters/{semester_id}", response_model=SemesterResponse)
def update_semester(
    semester_id: int,
    semester: SemesterUpdate,
    db: Session = Depends(get_db)
) -> SemesterResponse:
    """
    Update a semester's information.
    """
    return service.update_semester(db, semester_id, semester)

@router.delete("/semesters/{semester_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_semester(
    semester_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a semester.
    """
    service.delete_semester(db, semester_id) 