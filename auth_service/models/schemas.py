from sqlalchemy import Boolean, Column, Identity, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from decouple import config
from .setup import Base


class User(Base):
	__tablename__ = config("TABLE_NAME")

	id = Column(Integer, Identity("always"), primary_key=True, index=True, autoincrement=True)
	username = Column(String, index=True)
	password = Column(String)
	permissions = Column(JSON) 
	uuid = Column(String, index=True)