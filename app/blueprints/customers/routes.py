from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from . import customers_bp
from .schemas import customer_schema, customers_schema, login_schema
from app.models import Customer, ServiceTicket, db 
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required
from app.blueprints.service_tickets.schemas import service_tickets_schema



@customers_bp.route("", methods=['POST'])
@limiter.limit("5 per minute")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Email already associated with an account."}), 400

    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

@customers_bp.route("", methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_customers():
    try: 
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers.items), 200 

    except (TypeError, ValueError):
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers), 200

@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found."}), 404

@customers_bp.route("", methods=['PUT'])
@token_required
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200

@customers_bp.route("", methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f'Customer id: {customer_id}, successfully deleted.'}), 200

@customers_bp.route("/login", methods=['POST'])
@limiter.limit("5 per minute")  # Slows down anyone trying to guess passwords
def login():
    try:
        credentials = login_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == credentials['email'])
    customer = db.session.execute(query).scalar_one_or_none()

    if customer and customer.password == credentials['password']:
        token = encode_token(customer.id)
        return jsonify({
            "status": "success",
            "message": "Successfully logged in.",
            "auth_token": token
        }), 200

    return jsonify({"message": "Invalid email or password."}), 401

@customers_bp.route("/my-tickets", methods=['GET'])
@token_required
def get_my_tickets(customer_id):   # customer_id comes from the token, not the URL
    query = select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200
