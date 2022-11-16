from sqlalchemy.orm import Session
from sqlalchemy.sql import functions

from . import models, schemas


def get_file(db: Session, file_id: int):
	return db.query(models.File).filter(models.File.id == file_id).first()

def get_files(db: Session, skip: int = 0, limit: int = 100):
	return db.query(models.File).offset(skip).limit(limit).all()

def get_user_usage(db: Session, owner: str):
	return 0
#	return db.query(models.File).filter(models.File.owner == owner).all(functions.sum(models.File.size))

def create_file(db: Session, name: str, size: int, owner: str):
	db_user = models.File(name=name, size=size, owner=owner)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def delete_file(db: Session, id: int):
	return db.query(models.File).filter(models.File.id == id).delete()
