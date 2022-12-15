from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
import os

#SQLALCHEMY_DATABASE_URL = config('DATABASE_URL')
if os.getenv('KUBERNETES_SERVICE_HOST'):
  SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@solver-db.default.svc.cluster.local:5432/solver_service_database"
else:
  SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/solver_service_database"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
