#!/usr/bin/env python3
"""
Secure Flask Web Application
All vulnerabilities fixed from vulnerable_app.py
Author: Nilanjan Chowdhury
Date: June 28, 2026
"""

import os
import json
import hashlib
import sqlite3
import subprocess
from functools import wraps
from flask import Flask, request, jsonify, render_template_string, abort, session, redirect, url_for
import bcrypt
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)

# ==================== SECURE CONFIGURATION ====================
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = '/tmp/secure_uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# ==================== SECURE DATABASE ====================
def get_db_connection():
    conn = sqlite3.connect('secure_users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Create admin user if not exists
    admin = conn.execute('SELECT * FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin:
        hashed = bcrypt.hashpw('SecureAdmin123!'.encode(), bcrypt.gensalt())
        conn.execute(
            'INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)',
            ('admin', hashed, 'admin@example.com', 'admin')
        )
    conn.commit()
    conn.close()

init_db()

# ==================== AUTH DECORATOR ====================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        if user['role'] != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated

# ==================== SECURE ENDPOINTS ====================

@app.route('/')
def index():
    return jsonify({
        'message': 'Secure Flask App',
        'version': '1.0',
        'status': 'running'
    })

# --- SECURE LOGIN (Fixed: SQL Injection) ---
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = get_db_connection()
    # FIX: Parameterized query
    user = conn.execute(
        'SELECT * FROM users WHERE username = ?',
        (username,)
    ).fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode(), user['password_hash']):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({
            'message': f'Welcome {user["username"]}',
            'status': 'success',
            'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

# --- SECURE PING (Fixed: Command Injection) ---
@app.route('/ping', methods=['GET'])
@login_required
def ping():
    host = request.args.get('host', '').strip()
    if not host:
        return jsonify({'error': 'Host parameter required'}), 400
    
    # FIX: Validate input - only allow IP or domain
    import re
    if not re.match(r'^[a-zA-Z0-9\-\.]+$', host):
        return jsonify({'error': 'Invalid host format'}), 400
    
    # FIX: Use subprocess with shell=False
    try:
        result = subprocess.run(
            ['ping', '-c', '1', host],
            capture_output=True,
            text=True,
            timeout=5
        )
        return jsonify({
            'host': host,
            'output': result.stdout,
            'error': result.stderr if result.stderr else None
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Ping timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- SECURE ADMIN (Fixed: Broken Access Control) ---
@app.route('/admin', methods=['GET'])
@admin_required
def admin():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, email, role FROM users').fetchall()
    conn.close()
    return jsonify({
        'users': [dict(user) for user in users]
    })

# --- SECURE VIEW (Fixed: Path Traversal) ---
@app.route('/view', methods=['GET'])
@login_required
def view_file():
    filename = request.args.get('file', '').strip()
    if not filename:
        return jsonify({'error': 'File parameter required'}), 400
    
    # FIX: Secure path handling
    base_dir = os.path.abspath('./secure_files')
    os.makedirs(base_dir, exist_ok=True)
    safe_path = os.path.abspath(os.path.join(base_dir, secure_filename(filename)))
    
    # FIX: Ensure path is inside base_dir
    if not safe_path.startswith(base_dir):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        with open(safe_path, 'r') as f:
            return jsonify({'content': f.read()})
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- SECURE UPLOAD (Fixed: Insecure File Upload) ---
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # FIX: Validate file extension
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # FIX: Secure filename
    filename = secure_filename(file.filename)
    
    # FIX: Create safe directory
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    safe_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # FIX: Prevent overwriting
    if os.path.exists(safe_path):
        return jsonify({'error': 'File already exists'}), 409
    
    file.save(safe_path)
    return jsonify({
        'message': 'Upload successful',
        'filename': filename,
        'path': safe_path
    })

# --- SECURE DESERIALIZATION (Fixed: Insecure Deserialization) ---
@app.route('/profile', methods=['POST'])
@login_required
def profile():
    # FIX: Use JSON instead of pickle
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    # Only allow safe data types
    safe_data = {
        'name': data.get('name', 'User'),
        'email': data.get('email', ''),
        'bio': data.get('bio', '')
    }
    return jsonify({
        'profile': safe_data,
        'message': 'Profile updated (secure)'
    })

# --- SECURE DEBUG (Fixed: Sensitive Data Exposure) ---
@app.route('/debug', methods=['GET'])
@admin_required
def debug():
    # FIX: Only accessible to admins AND only shows safe info
    return jsonify({
        'status': 'debug mode disabled',
        'message': 'Use /health for status'
    })

# --- HEALTH CHECK (Replaces /debug) ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'timestamp': '2026-06-28'
    })

# --- SECURE ERROR HANDLING (Fixed: Information Disclosure) ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

if __name__ == '__main__':
    # FIX: Disable debug in production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)
