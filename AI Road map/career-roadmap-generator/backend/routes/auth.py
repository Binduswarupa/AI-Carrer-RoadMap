"""
Authentication Routes.
Handles user registration, login, and token verification.
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from bson import ObjectId
from functools import wraps
from config import Config

auth_bp = Blueprint('auth', __name__)


def get_db():
    """Lazy import to avoid circular imports."""
    from database import users_collection
    return users_collection


def token_required(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        try:
            data = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            users = get_db()
            current_user = users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({'error': 'Invalid token - user not found'}), 401
            current_user['_id'] = str(current_user['_id'])
            del current_user['password']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)
    return decorated


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    career_goal = data.get('career_goal', '').strip()

    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    users = get_db()

    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    user = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'career_goal': career_goal,
        'created_at': datetime.datetime.utcnow().isoformat(),
        'profile_complete': False,
        'skills': [],
        'education': '',
        'experience': ''
    }

    result = users.insert_one(user)

    token = jwt.encode({
        'user_id': str(result.inserted_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }, Config.JWT_SECRET, algorithm='HS256')

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': {
            'id': str(result.inserted_id),
            'name': name,
            'email': email,
            'career_goal': career_goal
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login an existing user."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400

    users = get_db()
    user = users.find_one({'email': email})

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }, Config.JWT_SECRET, algorithm='HS256')

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'career_goal': user.get('career_goal', '')
        }
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile."""
    return jsonify({
        'user': current_user
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update user profile."""
    data = request.get_json()
    users = get_db()

    update_fields = {}
    allowed_fields = ['name', 'career_goal', 'skills', 'education', 'experience']

    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]

    if update_fields:
        users.update_one(
            {'_id': ObjectId(current_user['_id'])},
            {'$set': update_fields}
        )

    return jsonify({'message': 'Profile updated successfully'}), 200


@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if the token is still valid."""
    return jsonify({
        'valid': True,
        'user': current_user
    }), 200
