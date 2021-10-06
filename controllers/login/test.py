import unittest
from unittest.mock import patch

from faker import Faker

from app import app, register_blueprints
from services.login import LoginService

register_blueprints()


class TestLoginController(unittest.TestCase):

    def setUp(self) -> None:
        self.client = app.test_client()
        self.fake = Faker()
        self.email = self.fake.email()
        self.password = self.fake.password()

    @patch.object(LoginService, 'login')
    def test_login(self, login_mock):
        expected = {
            'token': 'eyJ...'
        }

        params = {
            'email': self.email,
            'password': self.password
        }

        login_mock.return_value = expected

        response = self.client.post('/login', json=params)

        login_mock.assert_called_with(self.email, self.password)
        assert response.json == expected
        assert response.status_code == 200
