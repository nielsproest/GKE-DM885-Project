from sqlalchemy.orm import Session

from . import models, schemas


def get_file(db: Session, file_id: int):
	return db.query(models.File).filter(models.File.id == file_id).first()

def get_files(db: Session, skip: int = 0, limit: int = 100):
	return db.query(models.File).offset(skip).limit(limit).all()

def create_file(db: Session, name: str, owner: str):
	db_user = models.File(name=name, owner=owner)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def delete_file(db: Session, id: int):
	return db.query(models.File).filter(models.File.id == id).delete()
