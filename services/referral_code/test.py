import unittest
from unittest import mock

import flask
from alchemy_mock.mocking import UnifiedAlchemyMagicMock

import database
from app import app
from database.entities.referral_code import ReferralCode
from models.web.error_response import ErrorResponse
from services.referral_code import ReferralCodeService


class TestReferralCodeService(unittest.TestCase):

    @mock.patch.object(database, 'new_session')
    def test_share_no_referral_code(self, session):
        session.return_value = UnifiedAlchemyMagicMock(data=[
            (
                [mock.call.query(ReferralCode)],
                []
            )
        ])

        expected = (ErrorResponse('referral code not found'), 400)
        with app.test_request_context():
            r = ReferralCodeService().share('')
        assert 'errors' in r[0].json
        assert r[0].json['errors'] == list(expected[0].errors)
        assert r[1] == expected[1]

    @mock.patch.object(database, 'new_session')
    def test_share(self, session):
        model = ReferralCode(code='code', customer=1, will_credit_in=5)
        session.return_value = UnifiedAlchemyMagicMock(data=[
            (
                [mock.call.query(ReferralCode)],
                [model]
            )
        ])

        with app.test_request_context():
            response = ReferralCodeService().share('')

            expected = {
                'code': model.code,
                'link': f'{flask.request.host_url}signup?code={model.code}'
            }
            assert response.status_code == 200
            assert response.json == expected
