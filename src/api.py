from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base

# Import all controllers
from .controller.auth_controller import router as auth_router
from .controller.department_controller import router as department_router
from .controller.period_controller import router as period_router
from .controller.survey_controller import router as survey_router
from .controller.worker_controller import router as worker_router
from .controller.course_controller import router as course_router
from .controller.question_controller import router as question_router
from .controller.instructor_controller import router as instructor_router
from .controller.enrolling_controller import router as enrolling_router
from .controller.attendance_controller import router as attendance_router
from .controller.answer_controller import router as answer_router
from .controller.report_controller import router as report_router

# Create database tables (commented out to avoid connection errors on import)
# Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Cursito API",
    description="REST API for managing courses, workers, surveys, and more",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure this properly for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include all routers
app.include_router(auth_router)
app.include_router(department_router)
app.include_router(period_router)
app.include_router(survey_router)
app.include_router(worker_router)
app.include_router(course_router)
app.include_router(question_router)
app.include_router(instructor_router)
app.include_router(enrolling_router)
app.include_router(attendance_router)
app.include_router(answer_router)
app.include_router(report_router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Cursito API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
