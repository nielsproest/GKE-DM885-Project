from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from main import *

Base = declarative_base()

def uuid_helper():
  return str(uuid.uuid4())

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_helper)
    user_id = Column(UUID(as_uuid=True))
    mzn_id = Column(UUID(as_uuid=True))
    dzn_id = Column(UUID(as_uuid=True))
    result = Column(String)
    timeout = Column(Integer)
    status = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    solver_instances = relationship('SolverInstance')


class SolverInstance(Base):
    __tablename__ = 'solver_instances'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_helper)
    name = Column(String)
    image = Column(String)
    status = Column(String)
    result = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))

#    job = relationship("Job", back_populates="solver_instances")
