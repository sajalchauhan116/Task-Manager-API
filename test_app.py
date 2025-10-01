import pytest
import json
from app import app, db, User, Task
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_user():
    """Create a test user"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpassword')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers"""
    access_token = create_access_token(identity=test_user.id)
    return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def test_task(test_user):
    """Create a test task"""
    task = Task(
        title='Test Task',
        description='Test Description',
        user_id=test_user.id
    )
    db.session.add(task)
    db.session.commit()
    return task

class TestUserRegistration:
    def test_register_success(self, client):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        }
        response = client.post('/api/auth/register', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'newuser@example.com'

    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        data = {'username': 'newuser'}
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username"""
        data = {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123'
        }
        response = client.post('/api/auth/register',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Username already exists' in data['error']

class TestUserLogin:
    def test_login_success(self, client, test_user):
        """Test successful user login"""
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['user']['username'] == 'testuser'

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid credentials' in data['error']

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        data = {'username': 'testuser'}
        response = client.post('/api/auth/login',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

class TestTaskCRUD:
    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation"""
        data = {
            'title': 'New Task',
            'description': 'Task Description'
        }
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['task']['title'] == 'New Task'
        assert data['task']['description'] == 'Task Description'
        assert data['task']['completed'] == False

    def test_create_task_missing_title(self, client, auth_headers):
        """Test task creation without title"""
        data = {'description': 'Task Description'}
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Title is required' in data['error']

    def test_create_task_unauthorized(self, client):
        """Test task creation without authentication"""
        data = {'title': 'New Task'}
        response = client.post('/api/tasks',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 401

    def test_get_tasks_success(self, client, auth_headers, test_task):
        """Test getting all tasks"""
        response = client.get('/api/tasks', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['title'] == 'Test Task'
        assert data['count'] == 1

    def test_get_tasks_unauthorized(self, client):
        """Test getting tasks without authentication"""
        response = client.get('/api/tasks')
        assert response.status_code == 401

    def test_get_specific_task_success(self, client, auth_headers, test_task):
        """Test getting a specific task"""
        response = client.get(f'/api/tasks/{test_task.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['task']['title'] == 'Test Task'
        assert data['task']['id'] == test_task.id

    def test_get_specific_task_not_found(self, client, auth_headers):
        """Test getting a non-existent task"""
        response = client.get('/api/tasks/999', headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Task not found' in data['error']

    def test_update_task_success(self, client, auth_headers, test_task):
        """Test successful task update"""
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'completed': True
        }
        response = client.put(f'/api/tasks/{test_task.id}',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['task']['title'] == 'Updated Task'
        assert data['task']['completed'] == True

    def test_update_task_not_found(self, client, auth_headers):
        """Test updating a non-existent task"""
        data = {'title': 'Updated Task'}
        response = client.put('/api/tasks/999',
                            data=json.dumps(data),
                            content_type='application/json',
                            headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Task not found' in data['error']

    def test_delete_task_success(self, client, auth_headers, test_task):
        """Test successful task deletion"""
        response = client.delete(f'/api/tasks/{test_task.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Task deleted successfully' in data['message']

    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting a non-existent task"""
        response = client.delete('/api/tasks/999', headers=auth_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Task not found' in data['error']

    def test_user_isolation(self, client, test_user):
        """Test that users can only access their own tasks"""
        # Create another user
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        # Create task for other user
        other_task = Task(title='Other Task', user_id=other_user.id)
        db.session.add(other_task)
        db.session.commit()
        
        # Try to access other user's task
        access_token = create_access_token(identity=test_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get(f'/api/tasks/{other_task.id}', headers=headers)
        assert response.status_code == 404

class TestAPIEndpoints:
    def test_home_endpoint(self, client):
        """Test the home endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Task Manager API' in data['message']

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Endpoint not found' in data['error']

if __name__ == '__main__':
    pytest.main([__file__])

