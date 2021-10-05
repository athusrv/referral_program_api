from flask import Blueprint

from logger import logger
from models.web.error_response import ErrorResponse
from security import Claims, authenticated
from services.referral_code import ReferralCodeService

refcode = Blueprint('referral', __name__, url_prefix='/referral_code')


@refcode.route('', methods=['GET'])
@authenticated
def get():
    logger.info('get referral code request has been received')
    try:
        return ReferralCodeService().share(Claims.from_context().account_number)
    except Exception as err:
        logger.error(f'failed to share referral code due to an unexpected error: {err.__str__()}')
        return ErrorResponse('error processing your request').json()
