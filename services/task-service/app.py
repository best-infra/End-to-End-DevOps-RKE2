from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import pooling
import jwt
import os
import logging
from functools import wraps
from datetime import datetime

# CI/CD Pipeline Full Test - January 2026 v1.0.0 // // // //
# Task service with automated builds and security scanning
# Testing multi-service deployment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, 
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     expose_headers=['Content-Type', 'Authorization'])

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

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")

def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            logger.warning("No token provided in request")
            return jsonify({"error": "No token provided"}), 401
        
        try:
            token = token.split(' ')[1] if ' ' in token else token
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            request.user_id = payload['userId']
            logger.info(f"Token verified for user {request.user_id}")
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
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
def create_task():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority', 'medium')
    
    if not title or not description:
        logger.warning("Task creation failed: missing title or description")
        return jsonify({"error": "Title and description required"}), 400
    
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        logger.info(f"Creating task for user {request.user_id}: {title}")
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, priority) VALUES (%s, %s, %s, %s)",
            (request.user_id, title, description, priority)
        )
        conn.commit()
        task_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        logger.info(f"Task created successfully with ID {task_id}")
        return jsonify({"message": "Task created", "taskId": task_id}), 201
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return jsonify({"error": f"Failed to create task: {str(e)}"}), 500

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
def update_task(task_id):
    data = request.json
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    status = data.get('status')
    
    if not title or not description:
        return jsonify({"error": "Title and description required"}), 400
    
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        
        query = "UPDATE tasks SET title = %s, description = %s"
        params = [title, description]
        
        if priority:
            query += ", priority = %s"
            params.append(priority)
        
        if status:
            query += ", status = %s"
            params.append(status)
            
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
        logger.error(f"Error updating task: {e}")
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
        logger.error(f"Error toggling status: {e}")
        return jsonify({"error": "Failed to update status"}), 500

if __name__ == '__main__':
    logger.info("Starting task service...")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8002)))
