from app.extensions import ma
from app.models import ServiceTicket, ServiceInventory
from app.blueprints.mechanics.schemas import MechanicSchema
from app.blueprints.inventory.schemas import InventorySchema
from marshmallow import fields 

class EditTicketSchema(ma.Schema): 
    add_ids = fields.List(fields.Int(), required=True)
    remove_ids = fields.List(fields.Int(), required=True)

edit_ticket_schema = EditTicketSchema()

class ServiceInventorySchema(ma.SQLAlchemyAutoSchema):
    part = ma.Nested(InventorySchema)

    class Meta: 
        model = ServiceInventory
        fields = ('quantity', 'part')


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = ma.Nested(MechanicSchema, many=True, dump_only=True)
    part_links = ma.Nested(ServiceInventorySchema, many=True, dump_only=True)

    class Meta:
        model = ServiceTicket
        include_fk = True

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)