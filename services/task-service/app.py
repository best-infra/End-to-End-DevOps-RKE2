from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
import mysql.connector
from mysql.connector import pooling
import jwt
import os
import logging
from functools import wraps
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, validator
from typing import Optional

# CI/CD Pipeline Full Test - January 2026 v1.0.0 // // // //
# Task service with automated builds and security scanning
# Testing multi-service deployment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Trust proxy headers (behind ingress/nginx)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Enhanced CORS with specific origins
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
CORS(app, 
     supports_credentials=True,
     origins=allowed_origins if os.getenv('NODE_ENV') == 'production' else '*',
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type', 'Authorization'])

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per 15 minutes"],
    storage_uri="memory://"
)

# Pydantic models for validation
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    priority: str = Field(default='medium')
    
    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v

class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    priority: Optional[str] = None
    status: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None:
            allowed_priorities = ['low', 'medium', 'high']
            if v not in allowed_priorities:
                raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'completed']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

# Database connection pool //
db_config = {
    "host": os.getenv("DB_HOST", "mysql"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", "password"),
    "database": os.getenv("DB_NAME", "task_manager"),
    "pool_name": "task_pool",
    "pool_size": 5
}

# Initialize connection pool as None, will be created on first use
connection_pool = None

def get_connection_pool():
    """Lazy initialization of connection pool"""
    global connection_pool
    if connection_pool is None:
        try:
            logger.info("Creating MySQL connection pool...")
            connection_pool = pooling.MySQLConnectionPool(**db_config)
            logger.info("MySQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    return connection_pool

# Ensure JWT_SECRET is set
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    logger.critical("JWT_SECRET environment variable not set!")
    raise ValueError("JWT_SECRET must be set")

def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({"error": "No token provided"}), 401
        
        try:
            token = token.split(' ')[1] if ' ' in token else token
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user_id = payload['userId']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return jsonify({"error": "Authentication failed"}), 401
        
        return f(*args, **kwargs)
    
    return decorated

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "task-service"})

@app.route('/api/tasks', methods=['GET'])
@verify_token
def get_tasks():
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC",
            (request.user_id,)
        )
        tasks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(tasks)
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return jsonify({"error": "Failed to fetch tasks"}), 500

@app.route('/api/tasks', methods=['POST'])
@verify_token
@limiter.limit("20 per minute")
def create_task():
    try:
        # Validate input with Pydantic
        task_data = TaskCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()[0]['msg']}), 400
    except Exception:
        return jsonify({"error": "Invalid request data"}), 400
    
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, priority) VALUES (%s, %s, %s, %s)",
            (request.user_id, task_data.title, task_data.description, task_data.priority)
        )
        conn.commit()
        task_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        logger.info(f"Task created successfully with ID {task_id}")
        return jsonify({"message": "Task created", "taskId": task_id}), 201
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Failed to create task"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@verify_token
def delete_task(task_id):
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND user_id = %s",
            (task_id, request.user_id)
        )
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Task not found"}), 404
        
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Task deleted"})
    except Exception as e:
        print(f"Error deleting task: {e}")
        return jsonify({"error": "Failed to delete task"}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@verify_token
@limiter.limit("30 per minute")
def update_task(task_id):
    try:
        # Validate input with Pydantic
        task_data = TaskUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()[0]['msg']}), 400
    except Exception:
        return jsonify({"error": "Invalid request data"}), 400
    
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        query = "UPDATE tasks SET title = %s, description = %s"
        params = [task_data.title, task_data.description]
        
        if task_data.priority:
            query += ", priority = %s"
            params.append(task_data.priority)
        
        if task_data.status:
            query += ", status = %s"
            params.append(task_data.status)
            
        query += " WHERE id = %s AND user_id = %s"
        params.extend([task_id, request.user_id])
        
        cursor.execute(query, params)
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Task not found"}), 404
        
        cursor.close()
        conn.close()
        
        logger.info(f"Task {task_id} updated successfully")
        return jsonify({"message": "Task updated"})
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return jsonify({"error": "Failed to update task"}), 500

@app.route('/api/tasks/<int:task_id>/status', methods=['PATCH'])
@verify_token
def toggle_task_status(task_id):
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        # Get current status
        cursor.execute(
            "SELECT status FROM tasks WHERE id = %s AND user_id = %s",
            (task_id, request.user_id)
        )
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({"error": "Task not found"}), 404
        
        current_status = result[0]
        new_status = 'completed' if current_status == 'pending' else 'pending'
        
        # Update status
        cursor.execute(
            "UPDATE tasks SET status = %s WHERE id = %s AND user_id = %s",
            (new_status, task_id, request.user_id)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info(f"Task {task_id} status toggled to {new_status}")
        return jsonify({"message": "Status updated", "status": new_status})
    except Exception as e:
        logger.error(f"Error toggling status: {str(e)}")
        return jsonify({"error": "Failed to update status"}), 500

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Rate limit exceeded, please try again later"}), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting task service...")
    logger.info(f"Environment: {os.getenv('NODE_ENV', 'development')}")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8002)))
