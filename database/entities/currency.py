from enum import Enum

from sqlalchemy import Column, String

from database import Entity


class ECurrency(Enum):
    USD = 'USD'


class Currency(Entity):
    __tablename__ = 'currency'

    id = Column(String, primary_key=True)

    def __eq__(self, other):
        return isinstance(other, Currency) and self.id == other.id
