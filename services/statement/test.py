import datetime
import unittest
from unittest import mock

from alchemy_mock.mocking import UnifiedAlchemyMagicMock

import database
from app import app
from database.entities.statement import Statement
from models.web.statement_response import StatementSchema
from services.statement import StatementService


class TestStatementService(unittest.TestCase):

    @mock.patch.object(database, 'new_session')
    def test_empty_db(self, session):
        session.return_value = UnifiedAlchemyMagicMock()
        with app.test_request_context():
            response = StatementService().get('')
            assert response.status_code == 200
            assert response.json == []

    @mock.patch.object(database, 'new_session')
    def test_return_statement(self, session):
        accnum = '123141'
        query_result = [
            Statement(
                id=1,
                amount=10.0,
                description='',
                currency='USD',
                account=accnum,
                date=datetime.datetime.now()
            )
        ]

        session.return_value = UnifiedAlchemyMagicMock(data=[
            (
                [mock.call.query(Statement)],
                query_result
            ),
        ])

        with app.test_request_context():
            response = StatementService().get(accnum)
            assert response.status_code == 200
            assert response.json == StatementSchema(many=True).dump(query_result)
