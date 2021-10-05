import random
import string

from sqlalchemy.exc import IntegrityError, NoResultFound

from database import db_transaction
from database.entities.account import Account
from database.entities.currency import ECurrency
from database.entities.customer import Customer
from database.entities.referral_code import ReferralCode
from database.entities.statement import Statement
from logger import logger
from models.web.error_response import ErrorResponse
from security.password import PasswordUtils


class CustomerService:

    def signup(self, *args):
        name, email, password, referral_code = args
        # all the passwords will be encrypted using AES algorithm
        password = PasswordUtils().encrypt(password)

        try:
            with db_transaction() as txn:
                # create a new customer in the database
                customer = Customer(
                    name=name,
                    email=email,
                    password=password)
                txn.add(customer)
                txn.flush()

                # create an account for this customer and get the account number
                accnum = self._create_account(txn, customer.id)

                # also, create a unique referral code for this customer
                self._create_referral_code(txn, customer.id)

                if referral_code:
                    # if a referral code is provided, we check its existence and get it,
                    # otherwise, throw an error and rollback the database changes
                    # since we won't allow any sign up if the given referral code is invalid
                    rc = txn.query(ReferralCode).filter(ReferralCode.code == referral_code).one()

                    # well, if the referral code is about to issue a credit for its owner...
                    if rc.will_credit_in <= 1:
                        # we get the referral code owner's account
                        account = txn.query(Account).filter(Account.customer == rc.customer).one()
                        # and then we add a credit of $10.00 to his account
                        txn.add(Statement(
                            amount=10,
                            description='Credit due to referral code',
                            account=account.number
                        ))
                        # and we reset the counter
                        rc.will_credit_in = 5
                    else:
                        # if the referral code is not about to issue a credit, we decrease its counter
                        rc.will_credit_in -= 1

                    txn.flush()

                    # we also want to make sure that the person who signed up using a referral code get a $10.00 in credit
                    txn.add(Statement(
                        amount=10,
                        description='Credit due to a signup using a referral code',
                        account=accnum,
                        currency=ECurrency.USD.value
                    ))
                    txn.flush()

                # return an empty response with 201 HTTP status code (CREATED)
                return '', 201
        except IntegrityError as err:
            # there was a constraint violation, we log the details and send an error response
            err.hide_parameters = True  # hide_parameters = True to avoid the encrypted password to show up in the logs.
            logger.error(f'failed to create a new user due to an IntegrityError: {err.__str__()}')
            return ErrorResponse('invalid request', 'email must be unique').json()
        except NoResultFound as err:
            # an entity could not be found in the database
            # log the details and send an error response
            logger.error(f'failed to create a new user due to an NoResultsFound exception: {err.__str__()}')
            return ErrorResponse('referral code not found').json()

    def _create_account(self, txn, customer_id):
        while True:
            # generate an account number
            accnum = self._random_account_number()
            # check if it's already taken, otherwise break the loop (as Python does not have do...while)
            if not txn.query(Account).filter(Account.number == accnum).one_or_none():
                break

        # add the account in the database tied to the customer
        txn.add(Account(
            number=accnum,
            customer=customer_id
        ))
        txn.flush()
        return accnum

    def _create_referral_code(self, txn, customer_id):
        while True:
            # generate a random code
            code = self._random_referral_code()
            # check if it's already taken, otherwise break the loop (as Python does not have do...while)
            if not txn.query(ReferralCode).filter(ReferralCode.code == code).one_or_none():
                break

        # add the referral code in the database tied to the customer
        txn.add(ReferralCode(
            code=code,
            customer=customer_id
        ))
        txn.flush()
        return code

    def _random_account_number(self):
        return ''.join([str(random.randrange(0, 9, 1)) for _ in range(10)])

    def _random_referral_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
