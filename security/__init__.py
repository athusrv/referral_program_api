import os
from functools import wraps

import jwt
from flask import g as context, jsonify, request
from marshmallow import ValidationError

from logger import logger
from security.claims import Claims, ClaimsSchema


def authenticated(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        try:
            if token and ('Bearer' in token or 'bearer' in token):
                context.claims = ClaimsSchema().load(jwt.decode(token[7:], os.environ.get('JWT_SIGNING_KEY')))
            else:
                logger.error('token is not present or not a Bearer token')
                return jsonify({'error': 'Unauthorized'}), 401
        except ValidationError as err:
            logger.error(f'claims validation error: {err.__str__()}')
            return jsonify({'error': 'Unauthorized'}), 401
        except Exception as err:
            logger.error(err)
            return jsonify({'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)

    return wrapper
