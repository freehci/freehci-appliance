from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from .database import Base


class Vrf(Base):
    __tablename__ = "vrf"

    id = Column(Integer, primary_key=True, index=True)
    vrfId = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), nullable=False)
    rd = Column(String(32), nullable=True)
    description = Column(String(256), nullable=True)
    sections = Column(String(128), nullable=True)
    editDate = Column(TIMESTAMP, nullable=True, onupdate="CURRENT_TIMESTAMP")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
