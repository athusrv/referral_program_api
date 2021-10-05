import os
import unittest
from unittest import mock

from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from faker import Faker

import database
from database.entities.account import Account
from database.entities.customer import Customer
from database.entities.referral_code import ReferralCode
from database.entities.statement import Statement
from security.password import PasswordUtils
from services.customer import CustomerService


class TestCustomerService(unittest.TestCase):

    def setUp(self) -> None:
        os.environ.setdefault('ENC_KEY', '')

    @mock.patch.object(database, 'new_session')
    def test_simple_signup(self, session):
        session.return_value = UnifiedAlchemyMagicMock()

        name = 'User'
        email = 'user@email.com'
        password = 'password'

        with \
                mock.patch.object(CustomerService, '_random_account_number') as _random_account_number, \
                mock.patch.object(CustomerService, '_random_referral_code') as _random_referral_code, \
                mock.patch.object(PasswordUtils, 'encrypt') as encrypt:
            _random_account_number.return_value = '1234567890'
            _random_referral_code.return_value = 'A1B2C3D4E5'
            encrypt.return_value = password

            customer = Customer(name=name, email=email, password=password)
            account = Account(number=_random_account_number(), customer=1)
            rc = ReferralCode(code=_random_referral_code(), customer=1)

            CustomerService().signup(name, email, password, None)

            session.return_value.add.assert_has_calls([
                mock.call(customer),
                mock.call(account),
                mock.call(rc)
            ])

            c = session.return_value.query(Customer).filter(Customer.id == 1).one()
            assert c is not None
            assert c.name == name
            assert c.email == email
            assert c.password == password

    @mock.patch.object(database, 'new_session')
    def test_signup_with_referral_code(self, session):
        name = 'New User'
        email = 'newuser@email.com'
        password = ''

        # data for existing customer
        customer = Customer(id=1, name='User', email='user@email.com', password='')
        rc = ReferralCode(code='A1B2C3D4E5', customer=customer.id, will_credit_in=5)

        session.return_value = UnifiedAlchemyMagicMock(data=[
            (
                [mock.call.query(ReferralCode), mock.call.filter(ReferralCode.code == rc.code)],
                [rc]
            )
        ])

        with mock.patch.object(PasswordUtils, 'encrypt') as encrypt:
            encrypt.return_value = ''
            CustomerService().signup(name, email, password, rc.code)

            session.return_value.add.assert_has_calls([
                mock.call(Customer(name=name, email=email, password=password)),
            ])

            statement = session.return_value \
                .query(Statement) \
                .join(Account) \
                .join(Customer) \
                .filter(Statement.account == Account.number) \
                .filter(Account.customer == Customer.id) \
                .filter(Customer.email == email) \
                .one()

            assert statement is not None
            assert statement.amount == 10

    @mock.patch.object(database, 'new_session')
    def test_get_credit_after_five_signups(self, session):
        # data for existing customer
        customer = Customer(id=1, name='User', email='user@email.com', password='')
        account = Account(number='123456', customer=customer.id)
        rc = ReferralCode(code='A1B2C3D4E5', customer=customer.id, will_credit_in=5)

        # fake some data
        fake = Faker()
        customers = [(fake.name(), fake.email(), fake.password(), rc.code) for _ in range(5)]
        account_numbers = [fake.unique.random_int(min=1, max=999999) for _ in range(5)]
        referral_codes = [fake.unique.random_int(min=1, max=999999) for _ in range(5)]

        # fake the db session
        session.return_value = UnifiedAlchemyMagicMock(data=[
            (
                [mock.call.query(ReferralCode), mock.call.filter(ReferralCode.code == rc.code)],
                [rc]
            ),
            (
                [mock.call.query(Account), mock.call.filter(Account.customer == rc.customer)],
                [account]
            ),
            *[
                (
                    [mock.call.query(Account), mock.call.filter(Account.number == accnum)],
                    []
                )
                for accnum in account_numbers
            ],
            *[
                (
                    [mock.call.query(ReferralCode), mock.call.filter(ReferralCode.code == code)],
                    []
                )
                for code in referral_codes
            ]
        ])

        for i, c in enumerate(customers):
            # make sure we are faking the return of _random_account_number and _random_referral_code
            # to prevent the mocked Session to return data for unpredictable values
            with mock.patch.object(CustomerService, '_random_account_number') as _random_account_number, \
                    mock.patch.object(CustomerService, '_random_referral_code') as _random_referral_code:
                _random_account_number.return_value = account_numbers[i]
                _random_referral_code.return_value = referral_codes[i]

                # submit the signup request to the service
                CustomerService().signup(*c)

        # get all statements from the database
        statements = session.return_value \
            .query(Statement) \
            .filter(Statement.account == account.number) \
            .all()

        # make sure that we have len(customers) + 1 statements (1 for each new customer + 1 for the existing customer)
        assert len(statements) == len(customers) + 1

        # due to a limitation on the mocked Session class, we can not use the real .filter() function
        # so, let's get the statement of interested by using the pythonic way
        statement_of_interest = list(filter(lambda x: (x.account == account.number), statements))[0]

        # assert it's not null (None)
        assert statement_of_interest is not None
        # assert the amount is $10.00
        assert statement_of_interest.amount == 10.0
