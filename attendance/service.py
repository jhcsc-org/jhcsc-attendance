from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import qrcode
import io
import uuid

from models import (
    AttendanceSession,
    AttendanceRecord,
    AttendanceVerification,
    AttendanceAdjustment,
    AttendanceMethod,
    AttendanceStatus,
    Class,
    Student
)
from attendance.schemas import (
    AttendanceSessionCreate,
    AttendanceSessionUpdate,
    AttendanceRecordCreate,
    AttendanceAdjustmentCreate
)

class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    async def create_session(
        self,
        teacher_id: int,
        session_data: AttendanceSessionCreate
    ) -> AttendanceSession:
        """Create a new attendance session"""
        # Verify class exists and teacher has access
        class_exists = self.db.query(Class).filter(
            and_(
                Class.id == session_data.class_id,
                Class.teachers.any(id=teacher_id)
            )
        ).first()
        
        if not class_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class not found or access denied"
            )

        # Check for active session
        active_session = self.db.query(AttendanceSession).filter(
            and_(
                AttendanceSession.class_id == session_data.class_id,
                AttendanceSession.is_finalized == False
            )
        ).first()

        if active_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active session already exists for this class"
            )

        # Create session with appropriate settings based on method
        session = AttendanceSession(
            teacher_id=teacher_id,
            **session_data.model_dump()
        )

        if session_data.method == AttendanceMethod.QR_CODE:
            session.qr_code = self._generate_qr_code()
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def _generate_qr_code(self) -> str:
        """Generate a unique QR code for attendance session"""
        qr_data = f"attendance_{uuid.uuid4()}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr)
        img_byte_arr = img_byte_arr.getvalue()

        # Here you might want to save the image to a file system or cloud storage
        # For now, we'll just return the QR code data
        return qr_data

    async def get_session(self, session_id: int) -> Optional[AttendanceSession]:
        """Get attendance session by ID"""
        return self.db.query(AttendanceSession).filter(
            AttendanceSession.id == session_id
        ).first()

    async def update_session(
        self,
        session_id: int,
        teacher_id: int,
        update_data: AttendanceSessionUpdate
    ) -> AttendanceSession:
        """Update attendance session"""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        if session.teacher_id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this session"
            )

        if session.is_finalized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update finalized session"
            )

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(session, field, value)

        self.db.commit()
        self.db.refresh(session)
        return session

    async def record_attendance(
        self,
        session_id: int,
        record_data: AttendanceRecordCreate
    ) -> AttendanceRecord:
        """Record student attendance"""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        if session.is_finalized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is finalized"
            )

        # Verify student is enrolled in class
        student = self.db.query(Student).filter(
            and_(
                Student.id == record_data.student_id,
                Student.classes.any(id=session.class_id)
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found or not enrolled in this class"
            )

        # Check for existing record
        existing_record = self.db.query(AttendanceRecord).filter(
            and_(
                AttendanceRecord.session_id == session_id,
                AttendanceRecord.student_id == record_data.student_id
            )
        ).first()

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance already recorded for this student"
            )

        record = AttendanceRecord(
            session_id=session_id,
            recorded_at=datetime.utcnow(),
            **record_data.model_dump()
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    async def adjust_attendance(
        self,
        teacher_id: int,
        adjustment_data: AttendanceAdjustmentCreate
    ) -> AttendanceAdjustment:
        """Adjust an attendance record"""
        record = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.id == adjustment_data.record_id
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        # Verify teacher has access to this class
        session = await self.get_session(record.session_id)
        if session.teacher_id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to adjust this record"
            )

        # Create adjustment record
        adjustment = AttendanceAdjustment(
            record_id=record.id,
            adjusted_by_id=teacher_id,
            previous_status=record.status,
            **adjustment_data.model_dump(exclude={'record_id'})
        )

        # Update record status
        record.status = adjustment_data.new_status

        self.db.add(adjustment)
        self.db.commit()
        self.db.refresh(adjustment)
        return adjustment

    async def get_session_stats(self, session_id: int) -> Dict:
        """Get attendance statistics for a session"""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        records = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.session_id == session_id
        ).all()

        total_students = self.db.query(Student).filter(
            Student.classes.any(id=session.class_id)
        ).count()

        stats = {
            'total_students': total_students,
            'present_count': sum(1 for r in records if r.status == AttendanceStatus.PRESENT),
            'absent_count': sum(1 for r in records if r.status == AttendanceStatus.ABSENT),
            'late_count': sum(1 for r in records if r.status == AttendanceStatus.LATE),
            'excused_count': sum(1 for r in records if r.status == AttendanceStatus.EXCUSED),
        }
        
        stats['attendance_rate'] = (
            (stats['present_count'] + stats['late_count']) / total_students * 100
            if total_students > 0 else 0
        )

        return stats

    async def verify_attendance(
        self,
        session_id: int,
        verification_data: Dict
    ) -> bool:
        """Verify attendance based on session method"""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        if session.method == AttendanceMethod.QR_CODE:
            return verification_data.get('qr_code') == session.qr_code
        elif session.method == AttendanceMethod.FACE_RECOGNITION:
            # Face recognition verification will be implemented separately
            return False
        
        return False

    async def list_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        class_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[AttendanceSession]:
        """List attendance sessions with filters"""
        query = self.db.query(AttendanceSession)

        if class_id:
            query = query.filter(AttendanceSession.class_id == class_id)
        if teacher_id:
            query = query.filter(AttendanceSession.teacher_id == teacher_id)
        if is_active is not None:
            if is_active:
                query = query.filter(
                    and_(
                        AttendanceSession.is_finalized == False,
                        or_(
                            AttendanceSession.end_time == None,
                            AttendanceSession.end_time > datetime.utcnow()
                        )
                    )
                )
            else:
                query = query.filter(
                    or_(
                        AttendanceSession.is_finalized == True,
                        AttendanceSession.end_time <= datetime.utcnow()
                    )
                )

        return query.order_by(AttendanceSession.created_at.desc()).offset(skip).limit(limit).all()

    async def get_student_attendance_history(
        self,
        student_id: int,
        class_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AttendanceRecord]:
        """Get attendance history for a student"""
        query = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id
        )

        if class_id:
            query = query.join(AttendanceSession).filter(
                AttendanceSession.class_id == class_id
            )

        if start_date:
            query = query.filter(AttendanceRecord.recorded_at >= start_date)
        if end_date:
            query = query.filter(AttendanceRecord.recorded_at <= end_date)

        return query.order_by(AttendanceRecord.recorded_at.desc()).offset(skip).limit(limit).all()

    async def get_class_attendance_summary(
        self,
        class_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get attendance summary for a class"""
        # Get all students in the class
        students = self.db.query(Student).filter(
            Student.classes.any(id=class_id)
        ).all()

        # Base query for attendance records
        query = self.db.query(AttendanceRecord).join(AttendanceSession).filter(
            AttendanceSession.class_id == class_id
        )

        if start_date:
            query = query.filter(AttendanceRecord.recorded_at >= start_date)
        if end_date:
            query = query.filter(AttendanceRecord.recorded_at <= end_date)

        records = query.all()

        # Calculate statistics
        summary = {
            'class_id': class_id,
            'total_students': len(students),
            'total_sessions': self.db.query(AttendanceSession).filter(
                AttendanceSession.class_id == class_id
            ).count(),
            'attendance_by_status': {
                status.value: len([r for r in records if r.status == status])
                for status in AttendanceStatus
            },
            'student_summaries': []
        }

        # Calculate per-student statistics
        for student in students:
            student_records = [r for r in records if r.student_id == student.id]
            student_summary = {
                'student_id': student.id,
                'student_name': f"{student.first_name} {student.last_name}",
                'total_records': len(student_records),
                'status_counts': {
                    status.value: len([r for r in student_records if r.status == status])
                    for status in AttendanceStatus
                }
            }
            student_summary['attendance_rate'] = (
                (student_summary['status_counts']['present'] + 
                 student_summary['status_counts']['late']) / 
                summary['total_sessions'] * 100
                if summary['total_sessions'] > 0 else 0
            )
            summary['student_summaries'].append(student_summary)

        return summary

    async def bulk_record_attendance(
        self,
        session_id: int,
        records: List[AttendanceRecordCreate]
    ) -> List[AttendanceRecord]:
        """Record attendance for multiple students at once"""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        if session.is_finalized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is finalized"
            )

        created_records = []
        for record_data in records:
            try:
                record = await self.record_attendance(session_id, record_data)
                created_records.append(record)
            except HTTPException as e:
                # Log the error but continue processing other records
                print(f"Error recording attendance for student {record_data.student_id}: {e.detail}")

        return created_records

    async def get_student_attendance_rate(
        self,
        student_id: int,
        class_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Calculate attendance rate for a student"""
        query = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.student_id == student_id
        )

        if class_id:
            query = query.join(AttendanceSession).filter(
                AttendanceSession.class_id == class_id
            )

        if start_date:
            query = query.filter(AttendanceRecord.recorded_at >= start_date)
        if end_date:
            query = query.filter(AttendanceRecord.recorded_at <= end_date)

        records = query.all()
        total_sessions = len(records)

        if total_sessions == 0:
            return {
                'student_id': student_id,
                'total_sessions': 0,
                'attendance_rate': 0,
                'status_counts': {status.value: 0 for status in AttendanceStatus}
            }

        status_counts = {
            status.value: len([r for r in records if r.status == status])
            for status in AttendanceStatus
        }

        return {
            'student_id': student_id,
            'total_sessions': total_sessions,
            'attendance_rate': (
                (status_counts['present'] + status_counts['late']) / 
                total_sessions * 100
            ),
            'status_counts': status_counts
        } 