from datetime import datetime
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from attendance import service
from attendance.schemas import (
    AttendanceSessionCreate,
    AttendanceSessionUpdate,
    AttendanceSessionResponse,
    AttendanceSessionDetail,
    AttendanceRecordCreate,
    AttendanceRecordResponse,
    AttendanceAdjustmentCreate,
    AttendanceAdjustmentResponse,
    AttendanceStats
)
from attendance.export import ExportFormat, export_service

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("/sessions", response_model=AttendanceSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: AttendanceSessionCreate,
    teacher_id: int = Query(..., gt=0),
    db: Session = Depends(get_db)
) -> AttendanceSessionResponse:
    """
    Create a new attendance session.
    Requires teacher authentication.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.create_session(teacher_id, session_data)

@router.get("/sessions/{session_id}", response_model=AttendanceSessionDetail)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
) -> AttendanceSessionDetail:
    """
    Get detailed information about an attendance session.
    """
    attendance_service = service.AttendanceService(db)
    session = await attendance_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@router.get("/sessions", response_model=List[AttendanceSessionResponse])
async def list_sessions(
    class_id: Optional[int] = Query(None, gt=0),
    teacher_id: Optional[int] = Query(None, gt=0),
    is_active: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[AttendanceSessionResponse]:
    """
    List attendance sessions with optional filtering.
    """
    # TODO: Implement list_sessions in service
    pass

@router.patch("/sessions/{session_id}", response_model=AttendanceSessionResponse)
async def update_session(
    session_id: int,
    update_data: AttendanceSessionUpdate,
    teacher_id: int = Query(..., gt=0),
    db: Session = Depends(get_db)
) -> AttendanceSessionResponse:
    """
    Update an attendance session.
    Only the teacher who created the session can update it.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.update_session(session_id, teacher_id, update_data)

@router.post("/sessions/{session_id}/records", response_model=AttendanceRecordResponse)
async def record_attendance(
    session_id: int,
    record_data: AttendanceRecordCreate,
    db: Session = Depends(get_db)
) -> AttendanceRecordResponse:
    """
    Record attendance for a student in a session.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.record_attendance(session_id, record_data)

@router.post("/records/{record_id}/adjust", response_model=AttendanceAdjustmentResponse)
async def adjust_attendance(
    record_id: int,
    adjustment_data: AttendanceAdjustmentCreate,
    teacher_id: int = Query(..., gt=0),
    db: Session = Depends(get_db)
) -> AttendanceAdjustmentResponse:
    """
    Adjust an existing attendance record.
    Requires teacher authentication.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.adjust_attendance(teacher_id, adjustment_data)

@router.get("/sessions/{session_id}/stats", response_model=AttendanceStats)
async def get_session_stats(
    session_id: int,
    db: Session = Depends(get_db)
) -> AttendanceStats:
    """
    Get attendance statistics for a session.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.get_session_stats(session_id)

@router.post("/sessions/{session_id}/verify")
async def verify_attendance(
    session_id: int,
    verification_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """
    Verify attendance using the specified method (QR code, face recognition, etc.).
    """
    attendance_service = service.AttendanceService(db)
    is_verified = await attendance_service.verify_attendance(session_id, verification_data)
    return {
        "verified": is_verified,
        "message": "Attendance verified successfully" if is_verified else "Verification failed"
    }

@router.post("/sessions/{session_id}/finalize", response_model=AttendanceSessionResponse)
async def finalize_session(
    session_id: int,
    teacher_id: int = Query(..., gt=0),
    db: Session = Depends(get_db)
) -> AttendanceSessionResponse:
    """
    Finalize an attendance session.
    After finalization, no more attendance records can be added.
    """
    attendance_service = service.AttendanceService(db)
    update_data = AttendanceSessionUpdate(is_finalized=True)
    return await attendance_service.update_session(session_id, teacher_id, update_data)

@router.get("/sessions/{session_id}/qr-code")
async def get_session_qr_code(
    session_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get QR code for attendance session if QR code method is enabled.
    """
    attendance_service = service.AttendanceService(db)
    session = await attendance_service.get_session(session_id)
    if not session or not session.qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found for this session"
        )
    return {"qr_code": session.qr_code}

@router.get("/students/{student_id}/history", response_model=List[AttendanceRecordResponse])
async def get_student_attendance_history(
    student_id: int,
    class_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[AttendanceRecordResponse]:
    """
    Get attendance history for a specific student.
    Optional filtering by class and date range.
    """
    # TODO: Implement get_student_attendance_history in service
    pass 

@router.get("/classes/{class_id}/summary")
async def get_class_summary(
    class_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get attendance summary for a class.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.get_class_attendance_summary(
        class_id, start_date, end_date
    )

@router.post("/sessions/{session_id}/bulk", response_model=List[AttendanceRecordResponse])
async def bulk_record_attendance(
    session_id: int,
    records: List[AttendanceRecordCreate],
    db: Session = Depends(get_db)
) -> List[AttendanceRecordResponse]:
    """
    Record attendance for multiple students at once.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.bulk_record_attendance(session_id, records)

@router.get("/students/{student_id}/rate")
async def get_student_rate(
    student_id: int,
    class_id: Optional[int] = Query(None, gt=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get attendance rate for a student.
    """
    attendance_service = service.AttendanceService(db)
    return await attendance_service.get_student_attendance_rate(
        student_id, class_id, start_date, end_date
    )

@router.get("/export/session/{session_id}")
async def export_session_attendance(
    session_id: int,
    format: ExportFormat = Query(ExportFormat.RAW),
    include_student_info: bool = Query(True),
    include_class_info: bool = Query(True),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Export attendance data for a session.
    Returns formatted data that can be processed client-side.
    """
    attendance_service = service.AttendanceService(db)
    session = await attendance_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Get attendance records with related data
    records = await attendance_service.get_session_records_with_details(session_id)
    
    # Format data according to requested format
    return export_service.format_attendance_data(
        records,
        include_student_info=include_student_info,
        include_class_info=include_class_info
    )

@router.get("/export/student/{student_id}")
async def export_student_attendance(
    student_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    format: ExportFormat = Query(ExportFormat.RAW),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Export attendance history for a student.
    Returns formatted data that can be processed client-side.
    """
    attendance_service = service.AttendanceService(db)
    records = await attendance_service.get_student_attendance_history(
        student_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return export_service.format_attendance_data(
        records,
        include_student_info=True,
        include_class_info=True
    )