from sqlalchemy import Boolean, Column, Identity, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class File(Base):
	__tablename__ = "files"

	id = Column(Integer, Identity("always"), primary_key=True, index=True)
	name = Column(String, index=True)
	owner = Column(String) #GUID
	size = Column(Integer) #Bytes
