from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, logger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from registration.router import router as registration_router
from profiles.router import router as student_router
from classes.router import router as class_router
from academic.router import router as academic_router
from departments.router import router as department_router
from teachers.router import router as teacher_router
from attendance.router import router as attendance_router
from schedules.router import router as schedule_router
from camera.router import router as camera_router
from auth.route import router as auth_router
from auth.dependencies import get_current_user
from sqlalchemy.orm import Session
from database import init_db, close_db, get_db
from config import Settings
from database import db_manager

# NOTE: protected routes are routes that require a valid JWT token to access
PROTECTED_ROUTERS = [
    registration_router,
    student_router, 
    class_router,
    academic_router,
    department_router,
    teacher_router,
    attendance_router,
    schedule_router,
    camera_router
]

def register_protected_routes(app: FastAPI, routers: list):
    """Register multiple protected routes with common prefix and dependencies"""
    for router in routers:
        app.include_router(
            router,
            prefix="/api/v1",
            dependencies=[Depends(get_current_user)]
        )

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
app = FastAPI(
    title="Classifier",
    description="A facial recognition-based attendance system",
    version="1.0.0",
    lifespan=lifespan
)

settings = Settings()

@app.on_event("startup")
def on_startup():
    try:
        init_db()
        logger.info("Database initialized successfully.")
        db_manager.start_monitoring()
        logger.info("Started PostgreSQL connection monitoring.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

@app.on_event("shutdown")
def on_shutdown():
    close_db()

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "PostgreSQL" if settings.DATABASE_URL else "SQLite"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# protected routes registration
register_protected_routes(app, PROTECTED_ROUTERS)

# public routes registration
app.include_router(auth_router, prefix="/api/v1")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root(request: Request):
    """Serve the camera stream page"""
    return templates.TemplateResponse("camera.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)