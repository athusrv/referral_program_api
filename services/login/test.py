import os
import unittest
from unittest import mock

import jwt
from alchemy_mock.mocking import UnifiedAlchemyMagicMock

import database
from app import app
from database.entities.account import Account
from database.entities.customer import Customer
from models.web.error_response import ErrorResponse
from security import Claims, ClaimsSchema
from security.password import PasswordUtils
from services.login import LoginService


class TestLoginService(unittest.TestCase):

    def setUp(self) -> None:
        os.environ.setdefault('JWT_SIGNING_KEY', 'abf66892-254f-4413-9883-85166887d1bc')

    @mock.patch.object(database, 'new_session')
    def test_error(self, session):
        session.return_value = UnifiedAlchemyMagicMock()

        with app.test_request_context():
            expected = (ErrorResponse('Unauthorized'), 401)
            r = LoginService().login('user', 'password')
            assert 'errors' in r[0].json
            assert r[0].json['errors'] == list(expected[0].errors)
            assert r[1] == expected[1]

    @mock.patch.object(database, 'new_session')
    def test_success(self, session):
        accnum = '123141'
        name = 'User'
        email = 'user@email.com'
        password = 'password'
        encrypted_password = PasswordUtils().encrypt(password)

        claims = Claims.new(name, accnum)

        token = jwt.encode(
            ClaimsSchema().dump(claims),
            os.environ.get('JWT_SIGNING_KEY')
        ).decode()

        customer_query_result = Customer(id=1, name=name, email=email, password=encrypted_password)
        account_query_result = Account(number=accnum, customer=1)

        expected = {
            'token': token
        }

        session.return_value = UnifiedAlchemyMagicMock(data=[
            (
                [mock.call.query(Customer)],
                [customer_query_result]
            ),
            (
                [mock.call.query(Account)],
                [account_query_result]
            )
        ])

        with app.test_request_context():
            response = LoginService().login(email, password)
            assert response.status_code == 200
            assert response.json == expected
