import unittest
from datetime import datetime, timedelta

from faker import Faker

from app import app
from security import Claims
from security.claims import ClaimsValidationError


class TestClaims(unittest.TestCase):
    def setUp(self):
        self.fake = Faker()

    def test_create(self):
        name = self.fake.name()
        accnum = str(self.fake.unique.random_int())
        claims = Claims.new(name, accnum)

        assert claims.subject == name
        assert claims.account_number == accnum

    def test_valid(self):
        name = self.fake.name()
        accnum = str(self.fake.unique.random_int())
        claims = Claims.new(name, accnum)

        validation = claims.valid()
        assert validation[0]
        assert validation[1] is None

    def test_missing_sub(self):
        claims = Claims(
            issued_at=int(datetime.now().timestamp()),
            expiration_date=int((datetime.now() + timedelta(hours=3)).timestamp()),
            issuer=self.fake.name(),
            account_number=str(self.fake.unique.random_int())
        )

        validation = claims.valid()
        assert not validation[0]
        assert isinstance(validation[1], ClaimsValidationError)
        assert validation[1].err == 'missing required sub'

    def test_missing_issuer(self):
        claims = Claims(
            issued_at=int(datetime.now().timestamp()),
            expiration_date=int((datetime.now() + timedelta(hours=3)).timestamp()),
            subject=self.fake.name(),
            account_number=str(self.fake.unique.random_int())
        )

        validation = claims.valid()
        assert not validation[0]
        assert isinstance(validation[1], ClaimsValidationError)
        assert validation[1].err == 'missing required issuer'

    def test_missing_accnum(self):
        claims = Claims(
            issued_at=int(datetime.now().timestamp()),
            expiration_date=int((datetime.now() + timedelta(hours=3)).timestamp()),
            subject=self.fake.name(),
            issuer=self.fake.name()
        )

        validation = claims.valid()
        assert not validation[0]
        assert isinstance(validation[1], ClaimsValidationError)
        assert validation[1].err == 'missing required accnum'

    def test_context_claims(self):
        with app.test_request_context() as context:
            claims = Claims.new(self.fake.name(), str(self.fake.unique.random_int()))
            context.g.claims = claims

            from_context = Claims.from_context()

            assert claims.subject == from_context.subject
            assert claims.account_number == from_context.account_number
            assert claims.issuer == from_context.issuer
            assert claims.issued_at == from_context.issued_at
            assert claims.expiration_date == from_context.expiration_date

            assert Claims.has_context_claims()
