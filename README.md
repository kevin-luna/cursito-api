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
- **Auto-generated Documentation** - Interactive API docs at `/docs`

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

## Project Structure

```
src/
├── api.py                 # Main FastAPI application
├── database.py            # Database configuration
├── controller/            # API route controllers
│   ├── department_controller.py
│   ├── period_controller.py
│   ├── survey_controller.py
│   ├── worker_controller.py
│   ├── course_controller.py
│   ├── question_controller.py
│   ├── instructor_controller.py
│   ├── enrolling_controller.py
│   ├── attendance_controller.py
│   └── answer_controller.py
├── dto/                   # Pydantic DTOs
│   ├── department.py
│   ├── period.py
│   ├── survey.py
│   ├── worker.py
│   ├── course.py
│   ├── question.py
│   ├── instructor.py
│   ├── enrolling.py
│   ├── attendance.py
│   └── answer.py
├── model/                 # SQLAlchemy models
│   ├── department.py
│   ├── period.py
│   ├── survey.py
│   ├── worker.py
│   ├── course.py
│   ├── question.py
│   ├── instructor.py
│   ├── enrolling.py
│   ├── attendance.py
│   └── answer.py
└── repository/            # Repository pattern implementations
    ├── base.py
    ├── department_repository.py
    ├── period_repository.py
    ├── survey_repository.py
    ├── worker_repository.py
    ├── course_repository.py
    ├── question_repository.py
    ├── instructor_repository.py
    ├── enrolling_repository.py
    ├── attendance_repository.py
    └── answer_repository.py
```

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
