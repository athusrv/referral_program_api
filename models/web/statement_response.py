from marshmallow import Schema, fields


class StatementSchema(Schema):
    amount = fields.Float(required=True)
    description = fields.String()
    currency = fields.String(required=True)
    date = fields.DateTime(required=True)
