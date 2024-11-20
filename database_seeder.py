from datetime import datetime, date, time, timedelta
import random
from typing import List

from faker import Faker
from sqlalchemy.orm import Session

from database import SessionLocal, init_db
from models import (
    Base, Department, Program, SchoolYear, Semester, Schedule, Class,
    Teacher, Student, Room, ClassSchedule, AttendanceSession,
    AttendanceMethod, AttendanceStatus, AttendanceRecord
)

# Initialize Faker
fake = Faker()

def create_departments(db: Session, num_departments: int = 5) -> List[Department]:
    departments = []
    dept_names = ["Computer Science", "Engineering", "Business", "Arts", "Sciences"]
    
    for name in dept_names[:num_departments]:
        dept = Department(name=name)
        departments.append(dept)
        db.add(dept)
    
    db.commit()
    return departments

def create_programs(db: Session, departments: List[Department], num_programs: int = 10) -> List[Program]:
    programs = []
    program_names = [
        "Software Engineering", "Data Science", "Cybersecurity",
        "Mechanical Engineering", "Civil Engineering",
        "Business Administration", "Marketing",
        "Fine Arts", "Digital Media",
        "Physics", "Mathematics"
    ]
    
    for i in range(num_programs):
        program = Program(
            name=program_names[i],
            department_id=random.choice(departments).id
        )
        programs.append(program)
        db.add(program)
    
    db.commit()
    return programs

def create_school_years(db: Session) -> List[SchoolYear]:
    current_year = datetime.now().year
    school_years = []
    
    for year in range(current_year - 1, current_year + 2):
        school_year = SchoolYear(
            year_name=f"{year}-{year+1}",
            start_date=date(year, 9, 1),
            end_date=date(year + 1, 6, 30)
        )
        school_years.append(school_year)
        db.add(school_year)
    
    db.commit()
    return school_years

def create_semesters(db: Session, school_years: List[SchoolYear]) -> List[Semester]:
    semesters = []
    
    for school_year in school_years:
        # Fall semester
        fall = Semester(
            name="Fall",
            school_year_id=school_year.id,
            start_date=school_year.start_date,
            end_date=date(school_year.start_date.year, 12, 20)
        )
        # Spring semester
        spring = Semester(
            name="Spring",
            school_year_id=school_year.id,
            start_date=date(school_year.end_date.year, 1, 15),
            end_date=school_year.end_date
        )
        semesters.extend([fall, spring])
        db.add_all([fall, spring])
    
    db.commit()
    return semesters

def create_teachers(db: Session, num_teachers: int = 20) -> List[Teacher]:
    teachers = []
    
    for _ in range(num_teachers):
        teacher = Teacher(
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number()
        )
        teachers.append(teacher)
        db.add(teacher)
    
    db.commit()
    return teachers

def create_students(db: Session, num_students: int = 100) -> List[Student]:
    students = []
    
    for i in range(num_students):
        student = Student(
            student_id=f"STU{str(i+1).zfill(6)}",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=25),
            gender=random.choice(["Male", "Female", "Other"]),
            email=fake.email(),
            phone=fake.phone_number(),
            address=fake.address(),
            status="Active",
            enrollment_date=fake.date_between(start_date="-2y", end_date="today")
        )
        students.append(student)
        db.add(student)
    
    db.commit()
    return students

def create_rooms(db: Session, num_rooms: int = 15) -> List[Room]:
    rooms = []
    buildings = ["Main Building", "Science Complex", "Engineering Wing", "Arts Center"]
    
    for i in range(num_rooms):
        room = Room(
            name=f"Room {i+101}",
            capacity=random.randint(20, 40),
            building=random.choice(buildings),
            floor=random.randint(1, 4)
        )
        rooms.append(room)
        db.add(room)
    
    db.commit()
    return rooms

def create_classes(
    db: Session,
    programs: List[Program],
    semesters: List[Semester],
    teachers: List[Teacher],
    students: List[Student],
    rooms: List[Room],
    num_classes: int = 30
) -> List[Class]:
    classes = []
    
    for i in range(num_classes):
        # Create schedule
        schedule = Schedule(details=f"Schedule for Class {i+1}")
        db.add(schedule)
        db.flush()
        
        # Create class
        class_ = Class(
            name=f"Class {i+1}",
            program_id=random.choice(programs).id,
            schedule_id=schedule.id,
            semester_id=random.choice(semesters).id
        )
        db.add(class_)
        db.flush()
        
        # Assign teachers and students
        class_teachers = random.sample(teachers, k=random.randint(1, 3))
        class_students = random.sample(students, k=random.randint(15, 30))
        class_.teachers.extend(class_teachers)
        class_.students.extend(class_students)
        
        # Create class schedules
        for day in random.sample(range(5), k=2):  # Two days per week
            class_schedule = ClassSchedule(
                class_id=class_.id,
                room_id=random.choice(rooms).id,
                day_of_week=day,
                start_time=time(hour=random.randint(8, 16)),
                end_time=time(hour=random.randint(17, 20)),
                effective_from=semesters[0].start_date,
                effective_until=semesters[0].end_date
            )
            db.add(class_schedule)
        
        classes.append(class_)
    
    db.commit()
    return classes

def create_attendance_sessions(
    db: Session,
    classes: List[Class],
    num_sessions: int = 50
) -> List[AttendanceSession]:
    sessions = []
    
    for _ in range(num_sessions):
        class_ = random.choice(classes)
        teacher = random.choice(class_.teachers)
        
        start_time = datetime.now() - timedelta(days=random.randint(0, 30))
        session = AttendanceSession(
            class_id=class_.id,
            teacher_id=teacher.id,
            method=random.choice(list(AttendanceMethod)),
            start_time=start_time,
            end_time=start_time + timedelta(hours=2),
            is_finalized=True
        )
        db.add(session)
        db.flush()
        
        # Create attendance records for students
        for student in class_.students:
            record = AttendanceRecord(
                session_id=session.id,
                student_id=student.id,
                class_id=class_.id,
                status=random.choice(list(AttendanceStatus)),
                recorded_at=start_time + timedelta(minutes=random.randint(0, 15)),
                verification_method="manual"
            )
            db.add(record)
        
        sessions.append(session)
    
    db.commit()
    return sessions

def seed_database():
    """Initialize the database and seed it with sample data."""
    # Initialize the database (creates tables)
    init_db()
    
    # Create a new session
    db = SessionLocal()
    try:
        print("Seeding departments...")
        departments = create_departments(db)
        
        print("Seeding programs...")
        programs = create_programs(db, departments)
        
        print("Seeding school years...")
        school_years = create_school_years(db)
        
        print("Seeding semesters...")
        semesters = create_semesters(db, school_years)
        
        print("Seeding teachers...")
        teachers = create_teachers(db)
        
        print("Seeding students...")
        students = create_students(db)
        
        print("Seeding rooms...")
        rooms = create_rooms(db)
        
        print("Seeding classes...")
        classes = create_classes(db, programs, semesters, teachers, students, rooms)
        
        print("Seeding attendance sessions...")
        create_attendance_sessions(db, classes)
        
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database() 