from marshmallow import fields, Schema, ValidationError


class CustomerChurnRequestSchema(Schema):
    customerID     = fields.String(required=True)
    tenure         = fields.Float(required=True)
    TotalCharges   = fields.Float(required=True)
    Contract       = fields.String(required=True)
    PhoneService   = fields.String(required=True)