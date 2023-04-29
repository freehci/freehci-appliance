# File: models\customers_models.py
from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.orm import relationship
from .database import Base




class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    title = Column(String(128), nullable=False, default='', unique=True)
    address = Column(String(255), nullable=True)
    postcode = Column(String(32), nullable=True)
    city = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    lat = Column(String(31), nullable=True)
    long = Column(String(31), nullable=True)
    contact_person = Column(Text, nullable=True)
    contact_phone = Column(String(32), nullable=True)
    contact_mail = Column(String(254), nullable=True)
    note = Column(Text, nullable=True)
    status = Column(Enum('Active', 'Reserved', 'Inactive'), default='Active')

    ipaddresses = relationship("IPAddress", back_populates="customer")
    subnets = relationship("Subnet", back_populates="customer")
    vrfs = relationship("Vrf", back_populates="customer")
    vlans = relationship("VLAN", back_populates="customer")