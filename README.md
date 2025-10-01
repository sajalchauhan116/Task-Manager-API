# Task Manager API

A RESTful API for a simple task manager application built with Flask, featuring user authentication and CRUD operations for tasks.

## Features

- User registration and authentication with JWT tokens
- CRUD operations for tasks
- User-specific task management
- Input validation and error handling
- SQLite database (configurable)
- **Interactive Swagger Documentation**
- **Comprehensive Unit Tests**
- **API Demo Script**

## Quick Start

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   **Basic Version:**
   ```bash
   python app.py
   ```

   **Documented Version (with Swagger UI):**
   ```bash
   python app_with_docs.py
   ```

4. Access the API:
   - API Base URL: `http://localhost:5001`
   - Swagger Documentation: `http://localhost:5001/docs/` (documented version)

### Testing

Run the comprehensive test suite:
```bash
python run_tests.py
```

Or run specific tests:
```bash
pytest test_app.py -v
```

### Demo

Try the interactive demo:
```bash
python demo.py
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user

### Tasks (Requires Authentication)

- `GET /api/tasks` - Get all tasks for the authenticated user
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/<id>` - Get a specific task
- `PUT /api/tasks/<id>` - Update a task
- `DELETE /api/tasks/<id>` - Delete a task

## Usage Examples

### Register a new user
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "password123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "password123"}'
```

### Create a task (use the token from login response)
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"title": "Complete project", "description": "Finish the task manager API"}'
```

### Get all tasks
```bash
curl -X GET http://localhost:5000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Task Model

Each task has the following fields:
- `id` (auto-generated integer)
- `title` (string, required)
- `description` (text, optional)
- `completed` (boolean, default: false)
- `created_at` (timestamp)
- `updated_at` (timestamp)

## Documentation

### Interactive Documentation
The documented version (`app_with_docs.py`) provides interactive Swagger UI documentation at `http://localhost:5000/docs/` where you can:
- View all available endpoints
- See request/response schemas
- Test endpoints directly in the browser
- View example requests and responses

### API Documentation
Comprehensive API documentation is available in `API_DOCUMENTATION.md` with:
- Detailed endpoint descriptions
- Request/response examples
- Error handling information
- Usage examples in multiple languages

## Testing

### Test Coverage
The test suite includes comprehensive coverage for:
- ✅ User registration and authentication
- ✅ Task CRUD operations
- ✅ Authorization and user isolation
- ✅ Input validation
- ✅ Error handling
- ✅ Edge cases

### Running Tests
```bash
# Run all tests with coverage
python run_tests.py

# Run specific test class
pytest test_app.py::TestUserRegistration -v

# Run with detailed output
pytest test_app.py -v --tb=short
```

### Test Results
The test suite generates:
- Console output with test results
- HTML coverage report in `htmlcov/index.html`
- Detailed test reports

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error
# Task-Manager-API
