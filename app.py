from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory user store (for demo only)
USERS = {
    'admin': 'password123',
    'user': 'testpass'
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username in USERS and USERS[username] == password:
        return jsonify({'success': True, 'message': 'Login successful!'}), 200
    return jsonify({'success': False, 'message': 'Invalid credentials.'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required.'}), 400
    if username in USERS:
        return jsonify({'success': False, 'message': 'Username already exists.'}), 409
    USERS[username] = password
    return jsonify({'success': True, 'message': 'Registration successful!'}), 201

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('new_password')
    if not username or not new_password:
        return jsonify({'success': False, 'message': 'Username and new password required.'}), 400
    if username not in USERS:
        return jsonify({'success': False, 'message': 'User does not exist.'}), 404
    USERS[username] = new_password
    return jsonify({'success': True, 'message': 'Password reset successful!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
