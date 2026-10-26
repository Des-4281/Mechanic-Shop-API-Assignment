from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
from jose import jwt
import jose

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),  # expires 1 hour from now
        'iat': datetime.now(timezone.utc),                       # issued at
        'sub': str(customer_id)                                  # MUST be a string
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def encode_mechanic_token(mechanic_id): 
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),  # expires 1 hour from now
        'iat': datetime.now(timezone.utc), 
        'sub': str(mechanic_id), 
        'role': 'mechanic' 
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            customer_id = int(data['sub'])
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        return f(customer_id, *args, **kwargs)

    return decorated

def mechanic_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            customer_id = int(data['sub'])
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'message': 'Invalid token!'}), 401

        if data.get('role') != 'mechanic': 
            return jsonify({'message': 'Mechanics Only!'}), 403

        return f(customer_id, *args, **kwargs)

    return decorated