from flask import jsonify


class ErrorResponse:
    def __init__(self, *errors, **kwargs):
        self.errors = errors
        self.error_code = kwargs.get('error_code')
        if not self.error_code:
            self.error_code = 400

    def json(self):
        return jsonify(errors=self.errors), self.error_code
