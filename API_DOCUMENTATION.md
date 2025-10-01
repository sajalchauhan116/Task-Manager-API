# Task Manager API Documentation

## Overview

The Task Manager API is a RESTful web service built with Flask that provides user authentication and CRUD operations for managing tasks. The API supports two versions:

1. **Basic Version** (`app.py`) - Simple Flask API with JSON responses
2. **Documented Version** (`app_with_docs.py`) - Flask-RESTX API with Swagger documentation

## Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Task-Manager-API
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   
   **Basic Version:**
   ```bash
   python app.py
   ```
   
   **Documented Version (with Swagger UI):**
   ```bash
   python app_with_docs.py
   ```

4. **Access the API**
   - API Base URL: `http://localhost:5000`
   - Swagger Documentation: `http://localhost:5000/docs/` (documented version only)

## API Endpoints

### Authentication Endpoints

#### Register User
- **POST** `/api/auth/register`
- **Description:** Create a new user account
- **Request Body:**
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Response (201):**
  ```json
  {
    "message": "User created successfully",
    "access_token": "jwt_token_here",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00"
    }
  }
  ```

#### Login User
- **POST** `/api/auth/login`
- **Description:** Authenticate user and get access token
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response (200):**
  ```json
  {
    "message": "Login successful",
    "access_token": "jwt_token_here",
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00"
    }
  }
  ```

### Task Endpoints

All task endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

#### Get All Tasks
- **GET** `/api/tasks`
- **Description:** Retrieve all tasks for the authenticated user
- **Response (200):**
  ```json
  {
    "tasks": [
      {
        "id": 1,
        "title": "Complete project",
        "description": "Finish the task manager API",
        "completed": false,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
      }
    ],
    "count": 1
  }
  ```

#### Get Specific Task
- **GET** `/api/tasks/{id}`
- **Description:** Retrieve details of a specific task
- **Response (200):**
  ```json
  {
    "task": {
      "id": 1,
      "title": "Complete project",
      "description": "Finish the task manager API",
      "completed": false,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  }
  ```

#### Create Task
- **POST** `/api/tasks`
- **Description:** Create a new task
- **Request Body:**
  ```json
  {
    "title": "string",
    "description": "string (optional)"
  }
  ```
- **Response (201):**
  ```json
  {
    "message": "Task created successfully",
    "task": {
      "id": 1,
      "title": "New task",
      "description": "Task description",
      "completed": false,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  }
  ```

#### Update Task
- **PUT** `/api/tasks/{id}`
- **Description:** Update an existing task
- **Request Body:**
  ```json
  {
    "title": "string (optional)",
    "description": "string (optional)",
    "completed": "boolean (optional)"
  }
  ```
- **Response (200):**
  ```json
  {
    "message": "Task updated successfully",
    "task": {
      "id": 1,
      "title": "Updated task",
      "description": "Updated description",
      "completed": true,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  }
  ```

#### Delete Task
- **DELETE** `/api/tasks/{id}`
- **Description:** Delete a specific task
- **Response (200):**
  ```json
  {
    "message": "Task deleted successfully"
  }
  ```

## Error Responses

The API returns appropriate HTTP status codes and error messages:

- **400 Bad Request:** Invalid input data
- **401 Unauthorized:** Missing or invalid authentication
- **404 Not Found:** Resource not found
- **500 Internal Server Error:** Server error

Error response format:
```json
{
  "error": "Error message description"
}
```

## Testing

### Running Tests

1. **Run all tests:**
   ```bash
   python run_tests.py
   ```

2. **Run specific test:**
   ```bash
   python run_tests.py TestUserRegistration::test_register_success
   ```

3. **Run with pytest directly:**
   ```bash
   pytest test_app.py -v
   ```

4. **Run with coverage:**
   ```bash
   pytest test_app.py --cov=app --cov-report=html
   ```

### Test Coverage

The test suite covers:
- ✅ User registration and login
- ✅ Task CRUD operations
- ✅ Authentication and authorization
- ✅ Input validation
- ✅ Error handling
- ✅ User isolation (users can only access their own tasks)

### Test Structure

```
test_app.py
├── TestUserRegistration
│   ├── test_register_success
│   ├── test_register_missing_fields
│   └── test_register_duplicate_username
├── TestUserLogin
│   ├── test_login_success
│   ├── test_login_invalid_credentials
│   └── test_login_missing_fields
├── TestTaskCRUD
│   ├── test_create_task_success
│   ├── test_get_tasks_success
│   ├── test_update_task_success
│   ├── test_delete_task_success
│   └── test_user_isolation
└── TestAPIEndpoints
    ├── test_home_endpoint
    └── test_404_error
```

## Usage Examples

### Using cURL

1. **Register a user:**
   ```bash
   curl -X POST http://localhost:5000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "john_doe", "email": "john@example.com", "password": "password123"}'
   ```

2. **Login:**
   ```bash
   curl -X POST http://localhost:5000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "john_doe", "password": "password123"}'
   ```

3. **Create a task:**
   ```bash
   curl -X POST http://localhost:5000/api/tasks \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"title": "Complete project", "description": "Finish the task manager API"}'
   ```

4. **Get all tasks:**
   ```bash
   curl -X GET http://localhost:5000/api/tasks \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

### Using Python requests

```python
import requests

# Register
response = requests.post('http://localhost:5000/api/auth/register', json={
    'username': 'john_doe',
    'email': 'john@example.com',
    'password': 'password123'
})
print(response.json())

# Login
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'john_doe',
    'password': 'password123'
})
token = response.json()['access_token']

# Create task
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://localhost:5000/api/tasks', 
                        json={'title': 'New task'}, 
                        headers=headers)
print(response.json())

# Get tasks
response = requests.get('http://localhost:5000/api/tasks', headers=headers)
print(response.json())
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
DATABASE_URL=sqlite:///task_manager.db
```

### Database

The API uses SQLite by default, but can be configured to use other databases by changing the `DATABASE_URL` environment variable.

## Security Features

- JWT-based authentication
- Password hashing using Werkzeug
- User isolation (users can only access their own tasks)
- Input validation
- CORS support for frontend integration

## API Versions

### Basic Version (`app.py`)
- Simple Flask API
- JSON responses
- No documentation UI

### Documented Version (`app_with_docs.py`)
- Flask-RESTX integration
- Swagger UI at `/docs/`
- Interactive API documentation
- Request/response examples
- Model definitions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

