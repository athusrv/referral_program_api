from marshmallow import Schema, fields, post_load


class SignupRequest:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.password = kwargs.get('password')
        self.referral_code = kwargs.get('referral_code')


class SignupRequestSchema(Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
    referral_code = fields.String(data_key='referralCode', default=None)

    @post_load
    def _make(self, data, **kwargs):
        return SignupRequest(**data)
