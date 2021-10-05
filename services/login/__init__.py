import os

import jwt
from flask import jsonify
from sqlalchemy.exc import NoResultFound

from database import db_transaction
from database.entities.account import Account
from database.entities.customer import Customer
from logger import logger
from models.web.error_response import ErrorResponse
from security import Claims, ClaimsSchema
from security.password import PasswordUtils


class LoginService:

    def login(self, email, password):
        try:
            # yield a new database session so that we have a scope which a database transaction
            with db_transaction() as txn:
                # get this customer by email or throw a NoResultFound error
                customer = txn.query(Customer).filter(Customer.email == email).one()

                # check if the password matches
                if password != PasswordUtils().decrypt(customer.password):
                    # log the error
                    logger.error(f'wrong password for the user email {email}')
                    # and return an error response
                    return ErrorResponse('Unauthorized', error_code=401).json()

                # let get the customer's account so we have access to the account number
                # which is necessary for the JWT claims
                account = txn.query(Account).filter(Account.customer == customer.id).one()

                # create new claims
                claims = Claims.new(customer.name, account.number)
                # build a JWT
                token = jwt.encode(
                    ClaimsSchema().dump(claims),
                    os.environ.get('JWT_SIGNING_KEY', default='abf66892-254f-4413-9883-85166887d1bc')
                ).decode()

                # return it
                return jsonify(token=token)
        except NoResultFound as err:
            # the Customer could not be found in the database, so log the details and return a generic error
            logger.error(f'failed to login because the user email {email} could not be found in the database; details: {err.__str__()}')
            return ErrorResponse('Unauthorized', error_code=401).json()
        except Exception as err:
            # unexpected error
            raise err
