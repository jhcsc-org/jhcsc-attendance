from typing import Generator, Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from config import Settings
from models import Base
import os
import logging
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class DatabaseManager:
    def __init__(self):
        self.postgres_engine: Optional[Engine] = None
        self.sqlite_engine: Optional[Engine] = None
        self.current_engine: Optional[Engine] = None
        self.SessionLocal = None
        self._setup_engines()

    def _setup_engines(self) -> None:
        settings = Settings()
        if settings.DATABASE_URL:
            postgres_url = settings.DATABASE_URL
        else:
            postgres_url = (
                f"postgresql://{settings.SUPABASE_USER}:{settings.SUPABASE_PASSWORD}"
                f"@{settings.SUPABASE_HOST}:{settings.SUPABASE_PORT}/{settings.SUPABASE_DB}"
            )
        sqlite_url = f"sqlite:///data/{settings.DATABASE_LOCAL_NAME}"

        try:
            print(f"Constructed PostgreSQL URL: {postgres_url}")
            self.postgres_engine = create_engine(
                postgres_url,
                pool_size=5,
                max_overflow=10,
                echo=settings.DEBUG,
                pool_pre_ping=True
            )
            self.postgres_engine.connect()
            self.current_engine = self.postgres_engine
            logger.info("Connected to PostgreSQL database.")
        except OperationalError as e:
            logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
            self.postgres_engine = None
            self.sqlite_engine = create_engine(
                sqlite_url,
                echo=settings.DEBUG,
                connect_args={"check_same_thread": False}
            )
            self.current_engine = self.sqlite_engine
            logger.info("Connected to SQLite database.")

        self.SessionLocal = sessionmaker(
            bind=self.current_engine,
            autocommit=False,
            autoflush=False
        )

    def get_db(self) -> Generator[Session, None, None]:
        """Dependency for getting database sessions."""
        db = self.SessionLocal()
        try:
            yield db
        except OperationalError as e:
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            db.close()

    def init_db(self) -> None:
        """Initialize database tables."""
        try:
            Base.metadata.create_all(bind=self.current_engine)
            logger.info(f"Initialized {self._get_db_type()} database.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def close_db(self) -> None:
        """Cleanup database connections."""
        try:
            self.current_engine.dispose()
            logger.info(f"Closed connections to {self._get_db_type()} database.")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

    def _get_db_type(self) -> str:
        return "PostgreSQL" if self.current_engine == self.postgres_engine else "SQLite"

    def switch_to_sqlite(self) -> None:
        """Switch to SQLite manually."""
        if self.current_engine != self.sqlite_engine:
            logger.info("Switching to SQLite database.")
            self.current_engine = self.sqlite_engine
            self.SessionLocal.configure(bind=self.current_engine)

    def switch_to_postgres(self) -> None:
        """Attempt to switch back to PostgreSQL."""
        if self.postgres_engine:
            try:
                self.postgres_engine.connect()
                self.current_engine = self.postgres_engine
                self.SessionLocal.configure(bind=self.current_engine)
                logger.info("Switched back to PostgreSQL database.")
            except OperationalError as e:
                logger.error(f"Failed to reconnect to PostgreSQL: {e}")

    async def monitor_postgres_connection(self) -> None:
        """Continuously monitor PostgreSQL connection and attempt reconnection."""
        while True:
            if not self.postgres_engine:
                await asyncio.sleep(60)  # Wait before retrying
                try:
                    settings = Settings()
                    if settings.DATABASE_URL:
                        postgres_url = settings.DATABASE_URL
                    else:
                        postgres_url = (
                            f"postgresql://{settings.SUPABASE_USER}:{settings.SUPABASE_PASSWORD}"
                            f"@{settings.SUPABASE_HOST}:{settings.SUPABASE_PORT}/{settings.SUPABASE_DB}"
                        )
                    print(f"Constructed PostgreSQL URL: {postgres_url}")  # Add this line to debug
                    self.postgres_engine = create_engine(
                        postgres_url,
                        pool_size=5,
                        max_overflow=10,
                        echo=settings.DEBUG,
                        pool_pre_ping=True
                    )
                    self.postgres_engine.connect()
                    self.current_engine = self.postgres_engine
                    self.SessionLocal.configure(bind=self.current_engine)
                    logger.info("Reconnected to PostgreSQL database.")
                except OperationalError as e:
                    logger.warning(f"Reconnection to PostgreSQL failed: {e}. Retrying in 60 seconds.")
            await asyncio.sleep(60)  # Check every 60 seconds

    def start_monitoring(self) -> None:
        """Start the PostgreSQL connection monitoring task."""
        loop = asyncio.get_event_loop()
        loop.create_task(self.monitor_postgres_connection())

# Global instance
db_manager = DatabaseManager()
get_db = db_manager.get_db
init_db = db_manager.init_db
close_db = db_manager.close_db