from marshmallow import Schema, fields, post_load


class LoginRequest:
    def __init__(self, email, password):
        self.email = email
        self.password = password


class LoginRequestSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)

    @post_load
    def __make(self, data, **kwargs):
        return LoginRequest(**data)
