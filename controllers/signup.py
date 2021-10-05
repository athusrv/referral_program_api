from flask import Blueprint, render_template, request
from marshmallow import EXCLUDE, ValidationError

from logger import logger
from models.web.error_response import ErrorResponse
from models.web.signup_request import SignupRequestSchema
from services.customer import CustomerService

signup = Blueprint('user', __name__, url_prefix='/signup')


@signup.route('', methods=['POST'])
def create_customer():
    logger.info('signup request has been received')
    try:
        sr = SignupRequestSchema(unknown=EXCLUDE).load(request.get_json())

        return CustomerService().signup(sr.name, sr.email, sr.password, sr.referral_code)
    except ValidationError as err:
        logger.error(f'failed to create a new user because the payload is not a valid schema: {err.__str__()}')
        return ErrorResponse(err.normalized_messages()).json()
    except Exception as err:
        logger.err(f'failed to create a new customer because of a unexpected error: {err.__str__()}')
        return ErrorResponse('error processing your request')


@signup.route('', methods=['GET'])
def form():
    return render_template('signup.html')
