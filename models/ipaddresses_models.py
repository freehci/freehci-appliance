# File: ipaddresses_schemas.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, TIMESTAMP
from sqlalchemy.orm import relationship
from .database import Base


class IPAddress(Base):
    __tablename__ = "ipaddresses"

    id = Column(Integer, primary_key=True, index=True)
    subnetId = Column(Integer, ForeignKey("subnets.id"), nullable=True)
    ip_addr = Column(String(100), nullable=False)
    is_gateway = Column(Boolean, default=False, nullable=False)
    description = Column(String(64), nullable=True)
    hostname = Column(String(255), nullable=True)
    mac = Column(String(20), nullable=True)
    owner = Column(String(128), nullable=True)
    state = Column(Integer, nullable=True, default=2)
    #switch = Column(Integer, ForeignKey("switches.id"), nullable=True)
    location = Column(Integer, ForeignKey("locations.id"), nullable=True)
    port = Column(String(32), nullable=True)
    note = Column(String, nullable=True)
    lastSeen = Column(DateTime, nullable=True, default="1970-01-01 00:00:01")
    excludePing = Column(Boolean, default=False, nullable=False)
    PTRignore = Column(Boolean, default=False, nullable=False)
    PTR = Column(Integer, nullable=True, default=0)
    firewallAddressObject = Column(String(100), nullable=True)
    editDate = Column(TIMESTAMP, nullable=True, onupdate="CURRENT_TIMESTAMP")
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    subnet = relationship("Subnet", back_populates="ipaddresses")
    #switch = relationship("Switch", back_populates="ipaddresses")
    location = relationship("Location", back_populates="ipaddresses")
    customer = relationship("Customer", back_populates="ipaddresses")
