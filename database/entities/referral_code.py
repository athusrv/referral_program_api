from sqlalchemy import Column, ForeignKey, Integer, String

from database import Entity


class ReferralCode(Entity):
    __tablename__ = 'referral_code'

    code = Column(String, primary_key=True)
    will_credit_in = Column(Integer, nullable=False, default=5)
    customer = Column(Integer, ForeignKey('customer.id'))

    def __eq__(self, other):
        return isinstance(other, ReferralCode) and self.code == other.code
