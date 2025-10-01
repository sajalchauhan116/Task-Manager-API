from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///task_manager.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# Initialize Flask-RESTX
api = Api(
    app,
    version='1.0',
    title='Task Manager API',
    description='A RESTful API for managing tasks with user authentication',
    doc='/docs/',
    prefix='/api'
)

# Create namespaces
auth_ns = Namespace('auth', description='Authentication operations')
tasks_ns = Namespace('tasks', description='Task operations')

# Add namespaces to API
api.add_namespace(auth_ns)
api.add_namespace(tasks_ns)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# API Models for Swagger documentation
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp')
})

user_registration = api.model('UserRegistration', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password')
})

user_login = api.model('UserLogin', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

auth_response = api.model('AuthResponse', {
    'message': fields.String(description='Response message'),
    'access_token': fields.String(description='JWT access token'),
    'user': fields.Nested(user_model, description='User information')
})

task_model = api.model('Task', {
    'id': fields.Integer(readonly=True, description='Task ID'),
    'title': fields.String(required=True, description='Task title'),
    'description': fields.String(description='Task description'),
    'completed': fields.Boolean(description='Task completion status'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

task_create = api.model('TaskCreate', {
    'title': fields.String(required=True, description='Task title'),
    'description': fields.String(description='Task description')
})

task_update = api.model('TaskUpdate', {
    'title': fields.String(description='Task title'),
    'description': fields.String(description='Task description'),
    'completed': fields.Boolean(description='Task completion status')
})

task_response = api.model('TaskResponse', {
    'message': fields.String(description='Response message'),
    'task': fields.Nested(task_model, description='Task information')
})

tasks_response = api.model('TasksResponse', {
    'tasks': fields.List(fields.Nested(task_model), description='List of tasks'),
    'count': fields.Integer(description='Number of tasks')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

# Authentication Routes
@auth_ns.route('/register')
class UserRegistration(Resource):
    @api.expect(user_registration)
    @api.marshal_with(auth_response, code=201)
    @api.marshal_with(error_model, code=400)
    def post(self):
        """Register a new user"""
        try:
            data = request.get_json()
            
            if not data or not data.get('username') or not data.get('email') or not data.get('password'):
                return {'error': 'Username, email, and password are required'}, 400
            
            # Check if user already exists
            if User.query.filter_by(username=data['username']).first():
                return {'error': 'Username already exists'}, 400
            
            if User.query.filter_by(email=data['email']).first():
                return {'error': 'Email already exists'}, 400
            
            # Create new user
            user = User(
                username=data['username'],
                email=data['email']
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            # Generate access token
            access_token = create_access_token(identity=user.id)
            
            return {
                'message': 'User created successfully',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at
                }
            }, 201
            
        except Exception as e:
            return {'error': str(e)}, 500

@auth_ns.route('/login')
class UserLogin(Resource):
    @api.expect(user_login)
    @api.marshal_with(auth_response, code=200)
    @api.marshal_with(error_model, code=401)
    def post(self):
        """Login user"""
        try:
            data = request.get_json()
            
            if not data or not data.get('username') or not data.get('password'):
                return {'error': 'Username and password are required'}, 400
            
            user = User.query.filter_by(username=data['username']).first()
            
            if user and user.check_password(data['password']):
                access_token = create_access_token(identity=user.id)
                return {
                    'message': 'Login successful',
                    'access_token': access_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'created_at': user.created_at
                    }
                }, 200
            else:
                return {'error': 'Invalid credentials'}, 401
                
        except Exception as e:
            return {'error': str(e)}, 500

# Task Routes
@tasks_ns.route('')
class TaskList(Resource):
    @jwt_required()
    @api.marshal_with(tasks_response, code=200)
    @api.marshal_with(error_model, code=500)
    def get(self):
        """Get all tasks for the authenticated user"""
        try:
            user_id = get_jwt_identity()
            tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
            
            return {
                'tasks': [task.to_dict() for task in tasks],
                'count': len(tasks)
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @api.expect(task_create)
    @api.marshal_with(task_response, code=201)
    @api.marshal_with(error_model, code=400)
    def post(self):
        """Create a new task"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or not data.get('title'):
                return {'error': 'Title is required'}, 400
            
            task = Task(
                title=data['title'],
                description=data.get('description', ''),
                user_id=user_id
            )
            
            db.session.add(task)
            db.session.commit()
            
            return {
                'message': 'Task created successfully',
                'task': task.to_dict()
            }, 201
            
        except Exception as e:
            return {'error': str(e)}, 500

@tasks_ns.route('/<int:task_id>')
class TaskResource(Resource):
    @jwt_required()
    @api.marshal_with(task_model, code=200)
    @api.marshal_with(error_model, code=404)
    def get(self, task_id):
        """Get a specific task"""
        try:
            user_id = get_jwt_identity()
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            
            if not task:
                return {'error': 'Task not found'}, 404
            
            return task.to_dict(), 200
            
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @api.expect(task_update)
    @api.marshal_with(task_response, code=200)
    @api.marshal_with(error_model, code=404)
    def put(self, task_id):
        """Update a specific task"""
        try:
            user_id = get_jwt_identity()
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            
            if not task:
                return {'error': 'Task not found'}, 404
            
            data = request.get_json()
            
            if 'title' in data:
                task.title = data['title']
            if 'description' in data:
                task.description = data['description']
            if 'completed' in data:
                task.completed = data['completed']
            
            task.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'message': 'Task updated successfully',
                'task': task.to_dict()
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

    @jwt_required()
    @api.marshal_with(error_model, code=200)
    @api.marshal_with(error_model, code=404)
    def delete(self, task_id):
        """Delete a specific task"""
        try:
            user_id = get_jwt_identity()
            task = Task.query.filter_by(id=task_id, user_id=user_id).first()
            
            if not task:
                return {'error': 'Task not found'}, 404
            
            db.session.delete(task)
            db.session.commit()
            
            return {'message': 'Task deleted successfully'}, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

# Root route
@app.route('/')
def home():
    return jsonify({
        'message': 'Task Manager API',
        'version': '1.0',
        'documentation': '/docs/',
        'endpoints': {
            'auth': '/api/auth/',
            'tasks': '/api/tasks/'
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

