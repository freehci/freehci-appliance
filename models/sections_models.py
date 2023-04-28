from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, BINARY
from .database import Base


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    masterSection = Column(Integer, nullable=True, default=0)
    permissions = Column(String(1024), nullable=True)
    strictMode = Column(BINARY(1), nullable=False, default='1')
    subnetOrdering = Column(String(16), nullable=True)
    order = Column(Integer, nullable=True)
    editDate = Column(TIMESTAMP, nullable=True, onupdate="CURRENT_TIMESTAMP")
    showSubnet = Column(Boolean, nullable=False, default=True)
    showVLAN = Column(Boolean, nullable=False, default=False)
    showVRF = Column(Boolean, nullable=False, default=False)
    showSupernetOnly = Column(Boolean, nullable=False, default=False)
    DNS = Column(String(128), nullable=True)
