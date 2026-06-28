#!/usr/bin/env python3
"""
==========================================================
  VULNERABLE PYTHON WEB APPLICATION
  CodeAlpha — Task 3: Secure Coding Review
  !! FOR EDUCATIONAL PURPOSES ONLY !!
  This app contains intentional security vulnerabilities.
==========================================================
"""

from flask import Flask, request, jsonify, session
import sqlite3
import subprocess
import hashlib
import os
import pickle
import base64

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secret Key & Credentials
app.secret_key = "supersecretkey123"
DB_PASSWORD     = "admin123"
ADMIN_PASSWORD  = "password"
API_KEY         = "sk-1234567890abcdef"

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    password TEXT,
                    email TEXT
                )""")
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'password', 'admin@example.com')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'alice', '1234', 'alice@example.com')")
    conn.commit()
    conn.close()

# VULNERABILITY 2: SQL Injection
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    c.execute(query)
    user = c.fetchone()
    conn.close()
    if user:
        session["user"] = username
        return jsonify({"status": "success", "message": f"Welcome {username}"})
    return jsonify({"status": "fail", "message": "Invalid credentials"})

# VULNERABILITY 3: Command Injection
@app.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host")
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return result

# VULNERABILITY 4: Insecure File Upload
UPLOAD_FOLDER = "/tmp/uploads"

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if file:
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({"status": "uploaded", "path": filepath})
    return jsonify({"status": "error"})

# VULNERABILITY 5: Weak Cryptography
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    email    = request.form.get("email")
    hashed = hashlib.md5(password.encode()).hexdigest()
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(f"INSERT INTO users (username, password, email) VALUES ('{username}', '{hashed}', '{email}')")
    conn.commit()
    conn.close()
    return jsonify({"status": "registered"})

# VULNERABILITY 6: Insecure Deserialization
@app.route("/profile", methods=["GET"])
def profile():
    data = request.args.get("data")
    decoded = base64.b64decode(data)
    obj     = pickle.loads(decoded)
    return jsonify({"profile": str(obj)})

# VULNERABILITY 7: Sensitive Data Exposure
@app.route("/debug", methods=["GET"])
def debug():
    return jsonify({
        "secret_key":  app.secret_key,
        "db_password": DB_PASSWORD,
        "api_key":     API_KEY,
        "environment": dict(os.environ),
    })

# VULNERABILITY 8: Broken Access Control
@app.route("/admin", methods=["GET"])
def admin():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return jsonify({"all_users": users})

# VULNERABILITY 9: Path Traversal
@app.route("/read", methods=["GET"])
def read_file():
    filename = request.args.get("file")
    with open(filename, "r") as f:
        content = f.read()
    return content

# VULNERABILITY 10: Information Disclosure
@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute(f"SELECT * FROM users WHERE id={user_id}")
        user = c.fetchone()
        return jsonify({"user": user})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
