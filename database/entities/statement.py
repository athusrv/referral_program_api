import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from database import Entity
from database.entities.currency import ECurrency


class Statement(Entity):
    __tablename__ = 'statement'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    currency = Column(String, ForeignKey('currency.id'), default=ECurrency.USD.value)
    account = Column(String, ForeignKey('account.number'))
    date = Column(DateTime, default=datetime.datetime.now())

    def __eq__(self, other):
        return isinstance(other, Statement) and self.id == other.id
