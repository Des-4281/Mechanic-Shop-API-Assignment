# Mechanic Shop API

A REST API for a mechanic shop, built with Flask, SQLAlchemy, Marshmallow and MySQL. It manages customers, mechanics and service tickets, and lets you assign mechanics to tickets and remove them.

## Tech Stack

- Python 3.9
- Flask 3.1
- Flask-SQLAlchemy 3.1 / SQLAlchemy 2.0
- Flask-Marshmallow / marshmallow-sqlalchemy
- MySQL (via `mysql-connector-python`)

## Project Structure

```
Mechanic Shop Project/
├── app.py                      # Entry point: creates the app, creates tables, runs the server
├── config.py                   # DevelopmentConfig, TestingConfig, ProductionConfig
├── app/
│   ├── __init__.py             # create_app() factory, registers blueprints
│   ├── extensions.py           # Marshmallow instance
│   ├── models.py               # Customer, Mechanic, ServiceTicket, service_mechanics table
│   └── blueprints/
│       ├── customers/          # /customers routes and schemas
│       ├── mechanics/          # /mechanics routes and schemas
│       └── service_tickets/    # /service-tickets routes and schemas
└── tests/
```

## Setup

1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install Flask Flask-SQLAlchemy flask-marshmallow marshmallow-sqlalchemy mysql-connector-python python-dotenv
   ```

3. **Create the MySQL database**
   ```sql
   CREATE DATABASE mechanic_shop_db;
   ```

4. **Set your database connection.** Copy `.env.example` to `.env` and fill in your MySQL username and password:
   ```
   DATABASE_URL='mysql+mysqlconnector://<user>:<password>@localhost/mechanic_shop_db'
   ```
   `.env` is listed in `.gitignore`, so your credentials stay out of the repo.

5. **Run the app**
   ```bash
   python app.py
   ```
   The server starts at `http://127.0.0.1:5000`, and the tables are created automatically on first run.

## Data Model

- **Customer**: `id`, `name`, `email` (unique), `phone`
- **Mechanic**: `id`, `name`, `email` (unique), `phone`, `salary`
- **ServiceTicket**: `id`, `VIN` (max 17 chars), `service_date`, `service_desc`, `customer_id`
- **service_mechanics**: a join table linking service tickets and mechanics (many-to-many)

A customer can have many service tickets. A service ticket can have many mechanics, and a mechanic can work on many tickets.

## API Endpoints

Base URL: `http://127.0.0.1:5000`

### Customers

| Method | Endpoint | Description |
|---|---|---|
| POST | `/customers` | Create a customer |
| GET | `/customers` | Get all customers |
| GET | `/customers/<id>` | Get one customer |
| PUT | `/customers/<id>` | Update a customer |
| DELETE | `/customers/<id>` | Delete a customer |

Example body:
```json
{
  "name": "Jane Doe",
  "email": "jane@gmail.com",
  "phone": "321-555-0000"
}
```

### Mechanics

| Method | Endpoint | Description |
|---|---|---|
| POST | `/mechanics` | Create a mechanic |
| GET | `/mechanics` | Get all mechanics |
| PUT | `/mechanics/<id>` | Update a mechanic |
| DELETE | `/mechanics/<id>` | Delete a mechanic |

Example body:
```json
{
  "name": "Bob Smith",
  "email": "bob@shop.com",
  "phone": "555-1234",
  "salary": 55000
}
```

### Service Tickets

| Method | Endpoint | Description |
|---|---|---|
| POST | `/service-tickets` | Create a service ticket |
| GET | `/service-tickets` | Get all service tickets, including their assigned mechanics |
| PUT | `/service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>` | Assign a mechanic to a ticket |
| PUT | `/service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>` | Remove a mechanic from a ticket |

Example body (`customer_id` must belong to an existing customer):
```json
{
  "VIN": "1HGCM82633A004352",
  "service_date": "2026-10-14",
  "service_desc": "Oil change and tire rotation",
  "customer_id": 1
}
```

## Testing with Postman

Import `Mechanic Shop.postman_collection.json` into Postman. Its `base_url` variable is already set to `http://127.0.0.1:5000`. You can run the whole collection at once with the Collection Runner, starting from an empty database. Or send the requests one by one in this order, so each has the data it depends on:

1. Create Customer
2. Create Mechanic
3. Create Service Ticket
4. Assign Mechanic to Ticket
5. Get All Service Tickets (the mechanic shows up on the ticket)
6. Remove Mechanic From Ticket
7. Delete Mechanic


## License 
MIT 