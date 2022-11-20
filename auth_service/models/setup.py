import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from decouple import config

POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
POSTGRES_DB = config("POSTGRES_DB")
DATABASE_HOST = config("DATABASE_HOST")
DATABASE_PORT = config("DATABASE_PORT")

#TODO: For debugging, remove when confirmed working
print("User", POSTGRES_USER)
print("Password", POSTGRES_PASSWORD)
print("DB", POSTGRES_DB)

print("postgresql://{}:{}@{}:{}/{}".format(POSTGRES_USER,POSTGRES_PASSWORD,DATABASE_HOST,DATABASE_PORT,POSTGRES_DB))

#Expected to run in same cluster
SQLALCHEMY_DATABASE_URL = "postgresql://{}:{}@{}:{}/{}".format(POSTGRES_USER,POSTGRES_PASSWORD,DATABASE_HOST,DATABASE_PORT,POSTGRES_DB)

#engine = create_engine(
#	SQLALCHEMY_DATABASE_URL
#)
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#Base = declarative_base()


def get_database():
	return 1

#def get_database():
#	db = SessionLocal()
#	try:
#		yield db
#	finally:
#		db.close()