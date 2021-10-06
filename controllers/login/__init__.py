from flask import Blueprint, request
from marshmallow import EXCLUDE, ValidationError

from logger import logger
from models.web.error_response import ErrorResponse
from models.web.login_request import LoginRequestSchema
from services.login import LoginService

login = Blueprint('login', __name__, url_prefix='/login')


@login.route('', methods=['POST'])
def login_():
    logger.info('login request has been received')
    try:
        lr = LoginRequestSchema(unknown=EXCLUDE).load(request.get_json())

        return LoginService().login(lr.email, lr.password)
    except ValidationError as err:
        logger.error(f'failed to login because the payload is not a valid schema: {err.__str__()}')
        return ErrorResponse('Unauthorized', error_code=401).json()
    except Exception as err:
        logger.error(f'failed to login due to a unexpected error: {err.__str__()}')
        return ErrorResponse('Unauthorized', error_code=401).json()
