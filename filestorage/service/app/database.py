import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

#TODO: For debugging, remove when confirmed working
#print("User", POSTGRES_USER)
#print("Password", POSTGRES_PASSWORD)
#print("DB", POSTGRES_DB)

#Expected to run in same cluster
#TODO: Use DNS
SQLALCHEMY_DATABASE_URL = "postgresql://{}:{}@127.0.0.1:5432/{}".format(POSTGRES_USER,POSTGRES_PASSWORD,POSTGRES_DB)

engine = create_engine(
	SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
