
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')
    # Insert default users if not present
    for user, pwd in [('admin', 'password123'), ('user', 'testpass')]:
        c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', (user, pwd))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT username, password FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_password(username, new_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
    updated = c.rowcount
    conn.commit()
    conn.close()
    return updated > 0

@app.before_first_request
def setup():
    init_db()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = get_user(username)
    if user and user[1] == password:
        return jsonify({'success': True, 'message': 'Login successful!'}), 200
    return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required.'}), 400
    if get_user(username):
        return jsonify({'success': False, 'message': 'Username already exists.'}), 409
    if add_user(username, password):
        return jsonify({'success': True, 'message': 'Registration successful!'}), 201
    return jsonify({'success': False, 'message': 'Registration failed.'}), 500

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('new_password')
    if not username or not new_password:
        return jsonify({'success': False, 'message': 'Username and new password required.'}), 400
    if not get_user(username):
        return jsonify({'success': False, 'message': 'User does not exist.'}), 404
    if update_password(username, new_password):
        return jsonify({'success': True, 'message': 'Password reset successful!'}), 200
    return jsonify({'success': False, 'message': 'Password reset failed.'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
