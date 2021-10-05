from sqlalchemy import Column, Integer, String

from database import Entity


class Customer(Entity):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    def __eq__(self, other):
        return isinstance(other, Customer) and self.email == other.email
