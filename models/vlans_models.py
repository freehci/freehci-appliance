from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from .database import Base
from sqlalchemy.orm import relationship

class VLAN(Base):
    __tablename__ = "vlans"
    id = Column(Integer, primary_key=True, index=True)
    vlanId = Column(Integer, primary_key=True, index=True)
    domainId = Column(Integer, nullable=False, default=1)
    name = Column(String(255), nullable=False)
    number = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    editDate = Column(TIMESTAMP, nullable=True, onupdate="CURRENT_TIMESTAMP")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    customer = relationship("Customer", back_populates="vlans")
