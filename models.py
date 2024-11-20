from datetime import datetime, date, time
from typing import List, Optional
from enum import Enum

from sqlalchemy import Integer, String, Date, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Time
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RegistrationStep(str, Enum):
    PERSONAL_INFO = "personal_info"
    CONTACT_INFO = "contact_info"
    PROGRAM_SELECTION = "program_selection"
    DOCUMENT_UPLOAD = "document_upload"
    COMPLETED = "completed"

class Department(Base):
    __tablename__ = "departments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    programs: Mapped[List["Program"]] = relationship("Program", back_populates="department")

class Program(Base):
    __tablename__ = "programs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.id"))
    
    # Relationships
    department: Mapped[Department] = relationship("Department", back_populates="programs")
    classes: Mapped[List["Class"]] = relationship("Class", back_populates="program")

class SchoolYear(Base):
    __tablename__ = "school_years"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year_name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relationships
    semesters: Mapped[List["Semester"]] = relationship("Semester", back_populates="school_year")

class Semester(Base):
    __tablename__ = "semesters"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    school_year_id: Mapped[int] = mapped_column(Integer, ForeignKey("school_years.id"))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relationships
    school_year: Mapped[SchoolYear] = relationship("SchoolYear", back_populates="semesters")
    classes: Mapped[List["Class"]] = relationship("Class", back_populates="semester")

class Schedule(Base):
    __tablename__ = "schedules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    classes: Mapped[List["Class"]] = relationship("Class", back_populates="schedule")

class Class(Base):
    __tablename__ = "classes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    program_id: Mapped[int] = mapped_column(Integer, ForeignKey("programs.id"))
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("schedules.id"))
    semester_id: Mapped[int] = mapped_column(Integer, ForeignKey("semesters.id"))
    
    # Relationships
    program: Mapped[Program] = relationship("Program", back_populates="classes")
    schedule: Mapped[Schedule] = relationship("Schedule", back_populates="classes")
    semester: Mapped[Semester] = relationship("Semester", back_populates="classes")
    teachers: Mapped[List["Teacher"]] = relationship("Teacher", secondary="class_teachers")
    students: Mapped[List["Student"]] = relationship("Student", secondary="class_students")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="class_")
    schedules: Mapped[List["ClassSchedule"]] = relationship("ClassSchedule", back_populates="class_")
    attendance_sessions: Mapped[List["AttendanceSession"]] = relationship("AttendanceSession", back_populates="class_")

class Teacher(Base):
    __tablename__ = "teachers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30))
    
    # Relationships
    classes: Mapped[List[Class]] = relationship("Class", secondary="class_teachers")
    attendance_sessions: Mapped[List["AttendanceSession"]] = relationship("AttendanceSession", back_populates="teacher")

class Student(Base):
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20))
    address: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    enrollment_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relationships
    classes: Mapped[List[Class]] = relationship("Class", secondary="class_students")
    registration_sessions: Mapped[List["RegistrationSession"]] = relationship("RegistrationSession", back_populates="student")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship("AttendanceRecord", back_populates="student")

# Association tables for many-to-many relationships
class ClassTeachers(Base):
    __tablename__ = "class_teachers"
    
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"), primary_key=True)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id"), primary_key=True)

class ClassStudents(Base):
    __tablename__ = "class_students"
    
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"), primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), primary_key=True)

# Registration related models
class RegistrationSession(Base):
    __tablename__ = "registration_sessions"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), nullable=False)
    current_step: Mapped[RegistrationStep] = mapped_column(SQLEnum(RegistrationStep), nullable=False)
    completed_steps: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    student: Mapped[Student] = relationship("Student", back_populates="registration_sessions")
    personal_info: Mapped["RegistrationPersonalInfo"] = relationship("RegistrationPersonalInfo", back_populates="registration", uselist=False)
    contact_info: Mapped["RegistrationContactInfo"] = relationship("RegistrationContactInfo", back_populates="registration", uselist=False)
    documents: Mapped[List["RegistrationDocument"]] = relationship("RegistrationDocument", back_populates="registration")

class RegistrationPersonalInfo(Base):
    __tablename__ = "registration_personal_info"
    
    registration_id: Mapped[str] = mapped_column(String(50), ForeignKey("registration_sessions.id"), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Relationships
    registration: Mapped[RegistrationSession] = relationship("RegistrationSession", back_populates="personal_info")

class RegistrationContactInfo(Base):
    __tablename__ = "registration_contact_info"
    
    registration_id: Mapped[str] = mapped_column(String(50), ForeignKey("registration_sessions.id"), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    registration: Mapped[RegistrationSession] = relationship("RegistrationSession", back_populates="contact_info")

class RegistrationDocument(Base):
    __tablename__ = "registration_documents"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    registration_id: Mapped[str] = mapped_column(String(50), ForeignKey("registration_sessions.id"))
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    registration: Mapped[RegistrationSession] = relationship("RegistrationSession", back_populates="documents")


class AttendanceMethod(str, Enum):
    FACE_RECOGNITION = "face_recognition"
    QR_CODE = "qr_code"
    MANUAL = "manual"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"

class AttendanceSession(Base):
    """Represents an attendance collection session"""
    __tablename__ = "attendance_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id"), nullable=False)
    method: Mapped[AttendanceMethod] = mapped_column(SQLEnum(AttendanceMethod), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_finalized: Mapped[bool] = mapped_column(default=False)
    qr_code: Mapped[Optional[str]] = mapped_column(String(100))
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    class_: Mapped["Class"] = relationship("Class", back_populates="attendance_sessions")
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="attendance_sessions")
    records: Mapped[List["AttendanceRecord"]] = relationship(
        "AttendanceRecord", 
        back_populates="session",
        cascade="all, delete-orphan"
    )
    verifications: Mapped[List["AttendanceVerification"]] = relationship(
        "AttendanceVerification",
        back_populates="session",
        cascade="all, delete-orphan"
    )

class AttendanceRecord(Base):
    """Individual attendance record for a student"""
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("attendance_sessions.id"))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"))
    status: Mapped[AttendanceStatus] = mapped_column(SQLEnum(AttendanceStatus))
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    verification_method: Mapped[str] = mapped_column(String(50))
    verification_data: Mapped[Optional[dict]] = mapped_column(JSON)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    session: Mapped[AttendanceSession] = relationship("AttendanceSession", back_populates="records")
    student: Mapped["Student"] = relationship("Student", back_populates="attendance_records")
    class_: Mapped["Class"] = relationship("Class", back_populates="attendance_records")
    adjustments: Mapped[List["AttendanceAdjustment"]] = relationship(
        "AttendanceAdjustment",
        back_populates="record",
        cascade="all, delete-orphan"
    )

class AttendanceVerification(Base):
    """Verification data for attendance records"""
    __tablename__ = "attendance_verifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("attendance_sessions.id"))
    method: Mapped[str] = mapped_column(String(50))
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped[AttendanceSession] = relationship("AttendanceSession", back_populates="verifications")

class AttendanceAdjustment(Base):
    """Audit trail for attendance record adjustments"""
    __tablename__ = "attendance_adjustments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column(Integer, ForeignKey("attendance_records.id"))
    adjusted_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id"))
    previous_status: Mapped[AttendanceStatus] = mapped_column(SQLEnum(AttendanceStatus))
    new_status: Mapped[AttendanceStatus] = mapped_column(SQLEnum(AttendanceStatus))
    reason: Mapped[str] = mapped_column(Text)
    adjusted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    record: Mapped[AttendanceRecord] = relationship("AttendanceRecord", back_populates="adjustments")
    adjusted_by: Mapped["Teacher"] = relationship("Teacher") 
class Room(Base):
    __tablename__ = "rooms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    building: Mapped[str] = mapped_column(String(100), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    schedules: Mapped[List["ClassSchedule"]] = relationship("ClassSchedule", back_populates="room")

class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_until: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relationships
    class_: Mapped["Class"] = relationship("Class", back_populates="schedules")
    room: Mapped["Room"] = relationship("Room", back_populates="schedules")
    