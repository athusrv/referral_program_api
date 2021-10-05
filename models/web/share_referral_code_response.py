from marshmallow import Schema, fields


class ShareReferralCodeSchema(Schema):
    code = fields.String(required=True)
    link = fields.String(required=True)
