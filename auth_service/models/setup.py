""" Initialize Postgres Database """

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

POSTGRES_DB       = config("POSTGRES_DB")
DATABASE_HOST     = config("DATABASE_HOST") if os.getenv('KUBERNETES_SERVICE_HOST') else "0.0.0.0" # If running in kubernetes, use service name otherwise default to localhost
DATABASE_PORT     = config("DATABASE_PORT")
POSTGRES_USER     = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")



SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}"

engine = create_engine(
	SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_database():
	""" Get database connection """

	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


