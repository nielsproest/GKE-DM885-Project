from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base
  
def uuid_helper():
  return str(uuid.uuid4())

class Solver(Base):
    __tablename__ = "solver"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_helper)
    name = Column(String)
    dockerImage = Column(String)

# LAV MYSQLDB MODULET FRA TUTORIALEN I SIN EGEN FIL