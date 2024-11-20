from database import init_db
from models import Base
from sqlalchemy.orm import Session
from database import SessionLocal

def seed_data(db: Session) -> None:
    """Add initial seed data to the database."""
    pass

def main() -> None:
    """Initialize database and seed initial data."""
    print("Creating database tables...")
    init_db()
    print("Seeding initial data...")
    db = SessionLocal()
    try:
        seed_data(db)
        print("Database seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
