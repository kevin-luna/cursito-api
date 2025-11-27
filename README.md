# Cursito API

A comprehensive REST API built with FastAPI for managing courses, workers, surveys, and more. This API implements the repository pattern with SQLAlchemy and provides full CRUD operations for all entities.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Database support
- **Pydantic** - Data validation using Python type annotations
- **Repository Pattern** - Clean separation of data access logic
- **Comprehensive CRUD** - Full Create, Read, Update, Delete operations
- **Data Validation** - Input validation and error handling
- **Pagination** - Scalable endpoints ready to handle data intensive responses
- **JWT Authentication** - Access control for the REST Service
- **Auto-generated Documentation** - Interactive API docs at `/docs`

## Technology Stack & Library Selection

This section explains the key technologies and libraries chosen for this project, the problems they solve, and how they facilitate development.

### Core Framework

#### FastAPI
**Why chosen:**
- Modern Python web framework built on standard Python type hints
- Asynchronous request handling for high performance
- Automatic interactive API documentation (Swagger UI and ReDoc)
- Built-in data validation through Pydantic integration
- Excellent developer experience with auto-completion and type checking

**Problems it solves:**
- **Performance**: ASGI-based async support handles concurrent requests efficiently
- **Documentation**: Auto-generates OpenAPI specs, eliminating manual API documentation
- **Type Safety**: Leverages Python type hints for compile-time error detection
- **Validation**: Automatic request/response validation reduces boilerplate code
- **Developer Productivity**: Fast reload during development, clear error messages

**How it facilitates development:**
```python
# FastAPI automatically validates input and generates documentation
@router.post("/", response_model=DepartmentResponse)
def create_department(
    department: DepartmentCreate,  # Automatic validation
    db: Session = Depends(get_db)  # Dependency injection
):
    return repository.create(db, department)
```

### Database & ORM

#### SQLAlchemy
**Why chosen:**
- Most mature and feature-rich Python ORM
- Supports both high-level ORM and low-level SQL execution
- Excellent relationship mapping capabilities
- Database-agnostic (easy to switch databases)
- Strong community and extensive documentation

**Problems it solves:**
- **Database Abstraction**: Write Python code instead of raw SQL
- **Relationship Management**: Handles foreign keys, joins, and lazy loading automatically
- **Migration Safety**: Schema changes are trackable and reversible
- **Type Safety**: ORM models provide IDE auto-completion
- **SQL Injection Prevention**: Parameterized queries protect against injection attacks

**How it facilitates development:**
```python
# Define relationships declaratively
class Course(Base):
    __tablename__ = "courses"

    period_id = Column(UUID, ForeignKey("periods.id"))
    period = relationship("Period", back_populates="courses")

    # SQLAlchemy handles joins automatically
    # No need to write complex JOIN queries
```

#### PostgreSQL
**Why chosen:**
- ACID-compliant relational database with strong data integrity
- Advanced features: JSON support, full-text search, window functions
- Excellent performance for complex queries
- Open-source with no licensing costs
- Robust transaction support and concurrent access handling

**Problems it solves:**
- **Data Integrity**: Foreign keys, constraints, and transactions ensure data consistency
- **Scalability**: Handles large datasets and complex relationships efficiently
- **Reliability**: ACID compliance prevents data corruption
- **Advanced Queries**: Supports complex aggregations, CTEs, and analytical functions
- **Concurrent Access**: Multiple users can read/write simultaneously without conflicts

### Data Validation & Serialization

#### Pydantic
**Why chosen:**
- Native integration with FastAPI
- Runtime data validation using Python type hints
- Automatic data parsing and serialization
- Clear error messages for validation failures
- High performance (written in Rust core)

**Problems it solves:**
- **Input Validation**: Ensures only valid data enters the system
- **Type Coercion**: Automatically converts compatible types (e.g., string to UUID)
- **API Contracts**: DTOs serve as clear contracts between frontend and backend
- **Security**: Prevents over-posting and mass assignment attacks
- **Documentation**: Models auto-generate request/response schemas in API docs

**How it facilitates development:**
```python
class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=20)

    # Pydantic automatically:
    # - Validates name/code are strings
    # - Checks length constraints
    # - Returns clear error messages if invalid
    # - Generates JSON schema for API docs
```

### Server & Runtime

#### Uvicorn
**Why chosen:**
- Lightning-fast ASGI server implementation
- Supports HTTP/2 and WebSockets
- Efficient handling of async Python code
- Hot-reload during development
- Production-ready with proper signal handling

**Problems it solves:**
- **Performance**: Handles thousands of concurrent connections
- **Async Support**: Enables non-blocking I/O operations
- **Development Speed**: Auto-reload on code changes
- **Production Readiness**: Graceful shutdown, worker management

#### Python-dotenv
**Why chosen:**
- Simple environment variable management
- Keeps secrets out of version control
- Different configs for dev/staging/production
- Standard Python ecosystem tool

**Problems it solves:**
- **Security**: Database credentials and secrets stay out of code
- **Flexibility**: Easy to change configuration without code changes
- **Environment Separation**: Different settings for different deployment environments
- **12-Factor Compliance**: Follows best practices for cloud-native applications

**How it facilitates development:**
```python
# .env file (not committed to git)
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key

# Code reads from environment
from dotenv import load_dotenv
load_dotenv()

# No hardcoded secrets in source code
```

### Additional Dependencies

#### psycopg2-binary
- PostgreSQL adapter for Python
- Enables SQLAlchemy to communicate with PostgreSQL
- Handles connection pooling and query execution

#### python-multipart
- Parses multipart/form-data requests
- Required for file uploads and form submissions
- Integrates seamlessly with FastAPI

#### ReportLab
**Why chosen:**
- Industry-standard PDF generation library for Python
- Powerful layout and styling capabilities
- Supports tables, charts, and complex formatting
- Production-ready and well-maintained

**Problems it solves:**
- **PDF Generation**: Creates professional PDF reports programmatically
- **Data Presentation**: Formats complex data into readable documents
- **Automation**: Eliminates manual report creation
- **Consistency**: Ensures uniform document formatting

**How it facilitates development:**
```python
# Generate professional PDF reports
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

def generate_report(data):
    doc = SimpleDocTemplate("report.pdf")
    story = [
        Paragraph("Course Attendance", title_style),
        Table(data, style=custom_table_style)
    ]
    doc.build(story)
    return pdf_buffer
```

### Benefits of This Stack

1. **Type Safety Across Layers**: Python type hints → Pydantic → SQLAlchemy → PostgreSQL
2. **Automatic Validation**: Invalid data is rejected before reaching business logic
3. **Developer Experience**: Auto-completion, hot-reload, clear error messages
4. **Performance**: Async support, efficient ORM, optimized database
5. **Maintainability**: Clear separation of concerns, testable components
6. **Security**: SQL injection prevention, input validation, secret management
7. **Documentation**: Auto-generated, always up-to-date API docs
8. **Scalability**: Async architecture supports growth without major refactoring

## Architecture Overview

This API follows a **layered architecture** pattern with clear separation of concerns across four main layers:

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│         (Controllers/Routes)            │
├─────────────────────────────────────────┤
│         Business Logic Layer            │
│         (Service Layer - Future)        │
├─────────────────────────────────────────┤
│         Data Access Layer               │
│         (Repositories)                  │
├─────────────────────────────────────────┤
│         Data Layer                      │
│         (Models & Database)             │
└─────────────────────────────────────────┘
```

### Design Patterns

#### 1. Repository Pattern

The **Repository Pattern** provides an abstraction layer between the data access logic and the business logic. Each entity has its own repository that handles all database operations.

**Benefits:**
- Centralized data access logic
- Easy to test (repositories can be mocked)
- Decoupling of business logic from data access
- Consistent query interface across entities

**Implementation:**
- `BaseRepository` - Generic repository with common CRUD operations
- Entity-specific repositories extend `BaseRepository` and add specialized queries
- Repositories use SQLAlchemy sessions for database operations

```python
# Example: base.py
class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def get(self, db: Session, id: UUID) -> Optional[ModelType]
    def get_all(self, db: Session) -> List[ModelType]
    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType
    def update(self, db: Session, id: UUID, obj_in: UpdateSchemaType) -> ModelType
    def delete(self, db: Session, id: UUID) -> bool
```

#### 2. Data Transfer Object (DTO) Pattern

**Pydantic models** serve as DTOs to transfer data between layers and validate input/output.

**Benefits:**
- Strong type safety
- Automatic validation
- Clear API contracts
- Separation between database models and API schemas

**Implementation:**
- Each entity has Base, Create, Update, and response DTOs
- DTOs define what data can be sent/received through the API
- Validation rules are declarative using Pydantic

```python
# Example: department.py
class DepartmentBase(BaseModel):      # Shared fields
class DepartmentCreate(DepartmentBase):  # For POST requests
class DepartmentUpdate(BaseModel):    # For PUT requests
class Department(DepartmentBase):     # For responses
```

#### 3. Dependency Injection

FastAPI's built-in **dependency injection** system provides database sessions and repositories to controllers.

**Benefits:**
- Loose coupling between components
- Easier testing (dependencies can be overridden)
- Resource management (automatic session cleanup)

**Implementation:**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_all(db: Session = Depends(get_db)):
    repository = DepartmentRepository()
    return repository.get_all(db)
```

#### 4. Active Record Pattern (SQLAlchemy Models)

SQLAlchemy models combine data and behavior, representing database tables as Python classes.

**Benefits:**
- Object-oriented database interaction
- Rich relationship support
- Built-in validation and constraints

#### 5. Factory Pattern

Implicit use through SQLAlchemy and Pydantic model construction.

### Directory Structure

```
cursito-api/
├── src/
│   ├── api.py                      # FastAPI app initialization & route registration
│   ├── database.py                 # Database configuration & session management
│   │
│   ├── controller/                 # Presentation Layer - API endpoints
│   │   ├── department_controller.py
│   │   ├── period_controller.py
│   │   ├── worker_controller.py
│   │   ├── course_controller.py
│   │   ├── survey_controller.py
│   │   ├── question_controller.py
│   │   ├── instructor_controller.py
│   │   ├── enrolling_controller.py
│   │   ├── attendance_controller.py
│   │   └── answer_controller.py
│   │   # Controllers handle HTTP requests/responses and validation
│   │   # They delegate business logic to repositories
│   │
│   ├── dto/                        # Data Transfer Objects - API contracts
│   │   ├── department.py
│   │   ├── period.py
│   │   ├── worker.py
│   │   ├── course.py
│   │   ├── survey.py
│   │   ├── question.py
│   │   ├── instructor.py
│   │   ├── enrolling.py
│   │   ├── attendance.py
│   │   └── answer.py
│   │   # Pydantic models for request/response validation
│   │   # Define what data can enter/leave the API
│   │
│   ├── model/                      # Data Layer - Database schema
│   │   ├── department.py
│   │   ├── period.py
│   │   ├── worker.py
│   │   ├── course.py
│   │   ├── survey.py
│   │   ├── question.py
│   │   ├── instructor.py
│   │   ├── enrolling.py
│   │   ├── attendance.py
│   │   └── answer.py
│   │   # SQLAlchemy ORM models representing database tables
│   │   # Define relationships, constraints, and table structure
│   │
│   └── repository/                 # Data Access Layer - Query logic
│       ├── base.py                 # Generic CRUD operations
│       ├── department_repository.py
│       ├── period_repository.py
│       ├── worker_repository.py
│       ├── course_repository.py
│       ├── survey_repository.py
│       ├── question_repository.py
│       ├── instructor_repository.py
│       ├── enrolling_repository.py
│       ├── attendance_repository.py
│       └── answer_repository.py
│       # Repositories encapsulate all database queries
│       # Each extends BaseRepository with entity-specific queries
│
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── env_template.txt                # Environment variables template
└── README.md                       # This file
```

### Data Flow

A typical request flows through the layers as follows:

```
1. HTTP Request → Controller (Presentation Layer)
   ↓
2. Controller validates input using DTO (Pydantic)
   ↓
3. Controller calls Repository method (Data Access Layer)
   ↓
4. Repository queries Database using Model (Data Layer)
   ↓
5. Repository returns Model instance
   ↓
6. Controller converts Model to DTO (response schema)
   ↓
7. FastAPI serializes DTO to JSON
   ↓
8. HTTP Response ← Controller
```

**Example:**
```python
# 1. HTTP GET /workers/123
@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: UUID, db: Session = Depends(get_db)):
    # 2. No input validation needed for GET
    repository = WorkerRepository()

    # 3. Call repository method
    worker = repository.get(db, worker_id)

    # 4-5. Repository queries database and returns Worker model
    if not worker:
        raise HTTPException(status_code=404)

    # 6-7. FastAPI auto-converts Worker to WorkerResponse DTO
    return worker
```

### Key Architectural Decisions

#### Why Repository Pattern?

1. **Testability**: Repositories can be easily mocked in unit tests
2. **Maintainability**: All queries for an entity are in one place
3. **Flexibility**: Easy to switch databases or add caching
4. **Reusability**: Common queries are inherited from BaseRepository

#### Why Layered Architecture?

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **Scalability**: Easy to add new features without affecting existing code
3. **Maintainability**: Changes in one layer don't cascade to others
4. **Team Collaboration**: Different team members can work on different layers

#### Why DTOs (Pydantic)?

1. **Type Safety**: Compile-time type checking with mypy
2. **Auto-validation**: Invalid data is rejected automatically
3. **Documentation**: DTOs serve as API documentation
4. **Security**: Prevents over-posting attacks (mass assignment)

### Relationships & Foreign Keys

The database schema uses the following relationship patterns:

- **One-to-Many**: Department → Workers, Period → Courses, Survey → Questions, Course → Enrollments
- **Many-to-Many**: Courses ↔ Workers (through Instructors table), Courses ↔ Workers (through Enrolling table)
- **One-to-One**: Answer → Question (with composite unique constraint)

All foreign keys are enforced at the database level with appropriate `ON DELETE` behaviors.

## Database Schema

The API supports the following entities:

- **Departments** - Organizational departments
- **Periods** - Course periods with start/end dates
- **Surveys** - Survey definitions
- **Workers** - Staff members (teachers, department heads)
- **Courses** - Course information and scheduling
- **Questions** - Survey questions
- **Instructors** - Course instructors (many-to-many relationship)
- **Enrollings** - Worker course enrollments
- **Attendances** - Attendance tracking
- **Answers** - Survey responses

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cursito-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your database configuration
   ```

4. **Set up PostgreSQL database**
   - Create a PostgreSQL database
   - Update the `DATABASE_URL` in your `.env` file
   - Run the schema.sql file to create tables

5. **Run the application**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Endpoints

### Departments
- `GET /departments/` - List all departments
- `GET /departments/{id}` - Get department by ID
- `POST /departments/` - Create new department
- `PUT /departments/{id}` - Update department
- `DELETE /departments/{id}` - Delete department
- `GET /departments/search/{name}` - Search departments by name

### Periods
- `GET /periods/` - List all periods
- `GET /periods/{id}` - Get period by ID
- `POST /periods/` - Create new period
- `PUT /periods/{id}` - Update period
- `DELETE /periods/{id}` - Delete period
- `GET /periods/active/` - Get active periods
- `GET /periods/date-range/` - Get periods by date range

### Workers
- `GET /workers/` - List all workers
- `GET /workers/{id}` - Get worker by ID
- `POST /workers/` - Create new worker
- `PUT /workers/{id}` - Update worker
- `DELETE /workers/{id}` - Delete worker
- `GET /workers/department/{id}` - Get workers by department
- `GET /workers/role/{role}` - Get workers by role
- `GET /workers/search/{name}` - Search workers by name
- `GET /workers/email/{email}` - Get worker by email

### Courses
- `GET /courses/` - List all courses
- `GET /courses/{id}` - Get course by ID
- `POST /courses/` - Create new course
- `PUT /courses/{id}` - Update course
- `DELETE /courses/{id}` - Delete course
- `GET /courses/period/{id}` - Get courses by period
- `GET /courses/type/{type}` - Get courses by type
- `GET /courses/mode/{mode}` - Get courses by mode
- `GET /courses/profile/{profile}` - Get courses by profile
- `GET /courses/active/` - Get active courses
- `GET /courses/date-range/` - Get courses by date range
- `GET /courses/search/{name}` - Search courses by name

### And many more...

Each entity has comprehensive CRUD operations with additional specialized endpoints for common queries.

### Reports (PDF Generation)
- `GET /reports/attendance/{course_id}` - Download attendance list PDF for a course
- `GET /reports/enrollment/{worker_id}/{course_id}` - Download enrollment certificate PDF
- `GET /reports/instructor-courses/{worker_id}` - Download list of courses taught by instructor
- `GET /reports/survey/{worker_id}/{course_id}/followup` - Download follow-up survey responses PDF
- `GET /reports/survey/{worker_id}/{course_id}/opinion` - Download opinion survey responses PDF

All report endpoints return PDF files for download with comprehensive formatted information.

## Development

### Adding New Features

1. **Create Model**: Add SQLAlchemy model in `src/model/`
2. **Create DTOs**: Add Pydantic schemas in `src/dto/`
3. **Create Repository**: Implement repository in `src/repository/`
4. **Create Controller**: Add API routes in `src/controller/`
5. **Register Routes**: Include router in `src/api.py`

### Database Migrations

The application automatically creates tables on startup. For production, consider using Alembic for database migrations.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
