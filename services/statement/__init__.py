from operator import and_

from flask import jsonify

from database import db_transaction
from database.entities.account import Account
from database.entities.statement import Statement
from models.web.statement_response import StatementSchema


class StatementService:
    def get(self, accnum):
        try:
            # yield a new database session so that we have a scope which a database transaction
            with db_transaction() as txn:
                # get the statements associated with this account
                statement_lines = txn.query(Statement).join(Account).filter(
                    and_(
                        Statement.account == Account.number,
                        Account.number == accnum,
                    )
                ).all()

                # return them in a list
                return jsonify(StatementSchema(many=True).dump(statement_lines))
        except Exception as err:
            # unexpected error
            raise err
