from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from . import inventory_bp
from .schemas import inventory_schema, inventories_schema 
from app.models import ServiceTicket, Mechanic, Customer, Inventory, db
from app.utils.util import mechanic_token_required

@inventory_bp.route("", methods=['POST'])
@mechanic_token_required
def create_inventory(mechanic_id):
    try:
        part_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_part = Inventory(**part_data)
    db.session.add(new_part)
    db.session.commit()
    return inventory_schema.jsonify(new_part), 201

@inventory_bp.route("", methods=['GET'])
def get_parts():
    parts = db.session.execute(select(Inventory)).scalars().all()
    return inventories_schema.jsonify(parts), 200

@inventory_bp.route("/<int:inventory_id>", methods=['GET'])
def get_part(inventory_id):
    part = db.session.get(Inventory, inventory_id)
    if part: 
        return inventory_schema.jsonify(part), 200
    return jsonify({"error": "Part not found"}), 404
        
@inventory_bp.route("/<int:inventory_id>", methods=['PUT'])    
@mechanic_token_required
def update_part(mechanic_id, inventory_id):     
    part = db.session.get(Inventory, inventory_id)
    if not part:  
        return jsonify({"error": "Part not found"}), 404

    try: 
        part_data = inventory_schema.load(request.json) 
    except ValidationError as e: 
        return jsonify(e.messages), 400 

    for key, value in part_data.items():
        setattr(part, key, value)

    db.session.commit()
    return inventory_schema.jsonify(part), 200 

@inventory_bp.route("/<int:inventory_id>", methods=['DELETE'])
@mechanic_token_required
def delete_part(mechanic_id, inventory_id):
    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({"error": "Part not found"}), 404

    db.session.delete(part)
    db.session.commit()
    return jsonify({"message": f'Deleted - Part id: {inventory_id}'}), 200 

