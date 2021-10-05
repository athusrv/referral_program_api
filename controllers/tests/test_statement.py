import json
import os
import unittest
from unittest.mock import patch

import jwt
from faker import Faker

from app import app, register_blueprints
from security import Claims, ClaimsSchema
from services.statement import StatementService

register_blueprints()


class TestStatementController(unittest.TestCase):

    def setUp(self) -> None:
        self.client = app.test_client()
        self.fake = Faker()
        self.name = self.fake.name()
        self.accnum = str(self.fake.unique.random_int())
        os.environ.setdefault('JWT_SIGNING_KEY', self.fake.password())

    @patch.object(StatementService, 'get')
    def test_get_statement(self, statement_mock):
        token = jwt.encode(
            ClaimsSchema().dump(Claims.new(self.name, self.accnum)),
            os.environ.get('JWT_SIGNING_KEY')
        ).decode()

        expected = json.dumps([
            {
                'amount': 10.0,
                'description': '',
                'currency': 'USD'
            }
        ])

        statement_mock.return_value = expected

        response = self.client.get('/statement', headers={
            'Authorization': f'Bearer {token}'
        })

        statement_mock.assert_called_with(self.accnum)
        assert response.get_data(as_text=True) == expected
        assert response.status_code == 200
