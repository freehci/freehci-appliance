from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class Subnet(Base):
    __tablename__ = "subnets"

    id = Column(Integer, primary_key=True, index=True)
    subnet = Column(String(255), nullable=True)
    mask = Column(String(3), nullable=True)
    sectionId = Column(Integer, ForeignKey("sections.id"), nullable=True)
    description = Column(String, nullable=True)
    linked_subnet = Column(Integer, ForeignKey("subnets.id"), nullable=True)
    firewallAddressObject = Column(String(100), nullable=True)
    vrfId = Column(Integer, ForeignKey("vrf.id"), nullable=True)
    masterSubnetId = Column(Integer, nullable=False, default=0)
    allowRequests = Column(Boolean, default=False, nullable=False)
    vlanId = Column(Integer, ForeignKey("vlans.id"), nullable=True)
    showName = Column(Boolean, default=False, nullable=False)
    device = Column(Integer, nullable=True, default=0)
    permissions = Column(String(1024), nullable=True)
    pingSubnet = Column(Boolean, default=False, nullable=False)
    discoverSubnet = Column(Boolean, default=False, nullable=False)
    resolveDNS = Column(Boolean, default=False, nullable=False)
    DNSrecursive = Column(Boolean, default=False, nullable=False)
    DNSrecords = Column(Boolean, default=False, nullable=False)
    nameserverId = Column(Integer, nullable=True, default=0)
    scanAgent = Column(Integer, nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    isFolder = Column(Boolean, default=False, nullable=False)
    isFull = Column(Boolean, default=False, nullable=False)
    isPool = Column(Boolean, default=False, nullable=False)
    state = Column(Integer, nullable=True, default=2)
    threshold = Column(Integer, nullable=True, default=0)
    location = Column(Integer, ForeignKey("locations.id"), nullable=True)
    editDate = Column(TIMESTAMP, nullable=True, onupdate="CURRENT_TIMESTAMP")
    lastScan = Column(TIMESTAMP, nullable=True)
    lastDiscovery = Column(TIMESTAMP, nullable=True)

    linkedSubnet = relationship("Subnet", remote_side=[id], backref="linkedSubnets")
    customer = relationship("Customer", back_populates="subnets")
    section = relationship("Section", back_populates="subnets")
    vrf = relationship("VRF", back_populates="subnets")
    vlan = relationship("VLAN", back_populates="subnets")
    location = relationship("Location", back_populates="subnets")

