from sqlalchemy import Column, ForeignKey, Integer, String

from database import Entity


class Account(Entity):
    __tablename__ = 'account'

    number = Column(String, primary_key=True)
    customer = Column(Integer, ForeignKey('customer.id'))

    def __eq__(self, other):
        return isinstance(other, Account) and self.number == other.number
