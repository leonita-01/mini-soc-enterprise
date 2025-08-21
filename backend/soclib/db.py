from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, Index, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from ..settings import get_database_url
Base = declarative_base()
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    host = Column(String(128))
    src_ip = Column(String(64), index=True)
    dst_ip = Column(String(64))
    dst_port = Column(Integer)
    user = Column(String(128))
    http_path = Column(Text)
    status = Column(String(64))
    proto = Column(String(16))
    source_type = Column(String(64), index=True)
    raw = Column(Text)
    fields = Column(JSON)
Index("idx_events_src_ts", Event.src_ip, Event.ts)
class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    rule_id = Column(String(64), index=True)
    type = Column(String(64))
    severity = Column(String(16))
    src_ip = Column(String(64), index=True)
    dst_ip = Column(String(64))
    details = Column(JSON)
    status = Column(String(16), default="open")
    incident_id = Column(Integer, ForeignKey("incidents.id"))
class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    summary = Column(Text)
    status = Column(String(16), default="open")
    alerts = relationship("Alert", backref="incident")
class IOC(Base):
    __tablename__ = "iocs"
    id = Column(Integer, primary_key=True)
    ioc_type = Column(String(16))
    value = Column(String(255), index=True)
    source = Column(String(128))
class User(Base):
    __tablename__="users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(32), default="analyst")
    active = Column(Boolean, default=True)
class Audit(Base):
    __tablename__="audit"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow)
    actor = Column(String(255))
    action = Column(String(255))
    resource = Column(String(255))
    details = Column(JSON)
def get_engine():
    return create_engine(get_database_url(), future=True)
_engine = get_engine()
SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
def init_db():
    Base.metadata.create_all(_engine)

