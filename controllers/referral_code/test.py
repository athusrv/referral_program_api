import json
import os
import unittest
from unittest.mock import patch

import jwt
from faker import Faker

from app import app, register_blueprints
from security import Claims, ClaimsSchema
from services.referral_code import ReferralCodeService

register_blueprints()


class TestReferralCodeController(unittest.TestCase):

    def setUp(self) -> None:
        self.client = app.test_client()
        self.fake = Faker()
        self.name = self.fake.name()
        self.accnum = str(self.fake.unique.random_int())
        self.code = str(self.fake.unique.random_int())
        self.link = self.fake.url()
        os.environ.setdefault('JWT_SIGNING_KEY', self.fake.password())

    @patch.object(ReferralCodeService, 'share')
    def test_get_referral_code(self, share_mock):
        token = jwt.encode(
            ClaimsSchema().dump(Claims.new(self.name, self.accnum)),
            os.environ.get('JWT_SIGNING_KEY')
        ).decode()

        expected = {
            'code': self.code,
            'link': self.link
        }

        share_mock.return_value = expected

        response = self.client.get('/referral_code', headers={
            'Authorization': f'Bearer {token}'
        })

        share_mock.assert_called_with(self.accnum)
        assert json.loads(response.data.decode()) == expected
        assert response.status_code == 200
