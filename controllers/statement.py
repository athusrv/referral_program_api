from flask import Blueprint

from logger import logger
from models.web.error_response import ErrorResponse
from security import Claims, authenticated
from services.statement import StatementService

statement = Blueprint('statement', __name__, url_prefix='/statement')


@statement.route('', methods=['GET'])
@authenticated
def get_statement():
    logger.info('get statement request has been received')
    try:
        return StatementService().get(Claims.from_context().account_number)
    except Exception as err:
        logger.error(f'failed to get statement items due to a unexpected error: {err.__str__()}')
        return ErrorResponse('error processing your request').json()
