import unittest
from unittest.mock import patch

from faker import Faker

from app import app, register_blueprints
from services.customer import CustomerService

register_blueprints()


class TestSignUpController(unittest.TestCase):

    def setUp(self) -> None:
        self.client = app.test_client()
        self.fake = Faker()
        self.name = self.fake.name()
        self.email = self.fake.email()
        self.password = self.fake.password()
        self.referral_code = self.fake.password()

    @patch.object(CustomerService, 'signup')
    def test_signup_without_referral_code(self, signup_mock):
        expected = ('', 201)
        params = {
            'name': self.name,
            'email': self.email,
            'password': self.password
        }

        signup_mock.return_value = expected

        response = self.client.post('/signup', json=params)

        signup_mock.assert_called_with(self.name, self.email, self.password, None)
        assert response.data.decode() == expected[0]
        assert response.status_code == expected[1]

    @patch.object(CustomerService, 'signup')
    def test_signup_with_referral_code(self, signup_mock):
        expected = ('', 201)
        params = {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'referralCode': self.referral_code
        }

        signup_mock.return_value = expected

        response = self.client.post('/signup', json=params)

        signup_mock.assert_called_with(self.name, self.email, self.password, self.referral_code)
        assert response.data.decode() == expected[0]
        assert response.status_code == expected[1]
