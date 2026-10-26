from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema, mechanic_login_schema
from app.models import Mechanic, db
from app.extensions import limiter
from app.utils.util import encode_mechanic_token, mechanic_token_required

@mechanics_bp.route("", methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalars().all()
    if existing_mechanic:
        return jsonify({"error": "Email already associated with a mechanic."}), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_bp.route("", methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics), 200

@mechanics_bp.route("", methods=['PUT'])
@mechanic_token_required
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route("", methods=['DELETE'])
@mechanic_token_required
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404

    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f'Mechanic id: {mechanic_id}, successfully deleted.'}), 200

@mechanics_bp.route("/login", methods=['POST'])
@limiter.limit("5 per minute")  # Slows down anyone trying to guess passwords
def login():
    try:
        credentials = mechanic_login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Mechanic).where(Mechanic.email == credentials['email'])
    mechanic = db.session.execute(query).scalar_one_or_none()

    if mechanic and mechanic.password == credentials['password']:
        token = encode_mechanic_token(mechanic.id)
        return jsonify({
            "status": "success",
            "message": "Successfully logged in.",
            "auth_token": token
        }), 200

    return jsonify({"message": "Invalid email or password."}), 401

@mechanics_bp.route("/most-tickets", methods=['GET'])
def get_mechanic_by_tickets():
    mechanics = db.session.execute(select(Mechanic)).scalars().all()
    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    return mechanics_schema.jsonify(mechanics), 200