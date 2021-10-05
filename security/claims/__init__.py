from datetime import datetime, timedelta

from flask import g as context
from marshmallow import Schema, fields, post_load


class ClaimsValidationError:
    def __init__(self, err: str):
        self.err = err

    def __str__(self):
        return self.err


class Claims:
    def __init__(self, **kwargs):
        self.subject = kwargs.get('subject')
        self.issued_at = kwargs.get('issued_at')
        self.expiration_date = kwargs.get('expiration_date')
        self.issuer = kwargs.get('issuer')
        self.account_number = kwargs.get('account_number')

    def valid(self) -> (bool, ClaimsValidationError):
        if not self.subject or len(self.subject) == 0:
            return False, ClaimsValidationError('missing required sub')
        if not self.issuer or len(self.issuer) == 0:
            return False, ClaimsValidationError('missing required issuer')
        if not self.account_number or len(self.account_number) == 0:
            return False, ClaimsValidationError('missing required accnum')

        return True, None

    @staticmethod
    def from_context():
        claims = context.get('claims', default=None)
        if not claims:
            raise RuntimeError('no claims found in the context')
        return Claims(**claims.__dict__)

    @staticmethod
    def has_context_claims():
        claims = context.get('claims', default=None)
        if not claims:
            return False
        return True

    @staticmethod
    def new(subject, account_number):
        return Claims(
            subject=subject,
            issued_at=int(datetime.now().timestamp()),
            expiration_date=int((datetime.now() + timedelta(hours=3)).timestamp()),
            issuer='Referral Program API',
            account_number=account_number,
        )


class ClaimsSchema(Schema):
    subject = fields.String(data_key='sub', required=True)
    issued_at = fields.Number(data_key='iat', required=True)
    expiration_date = fields.Number(data_key='exp', required=True)
    issuer = fields.String(data_key='iss', required=True)
    account_number = fields.String(data_key='accnum', required=True)

    @post_load
    def make_claims(self, data, **kwargs):
        return Claims(**data)
