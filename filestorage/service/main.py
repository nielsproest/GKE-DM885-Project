from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from os.path import join

#TODO: Pydantic Schemas for returning data consistently
from . import crud, models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

#Where our files are stored
OS_DIR = "/mnt/data"

@app.post("/")
async def write(file: UploadFile, db: Session = Depends(get_db)):
	#TODO: Limit size to prevent exploitation
	fs = await file.read()
	fs_size = len(fs)
	
	#TODO: Check user space available
	#if (crud.get_user_usage(db, None) > 500):
	#	raise HTTPException(status_code=413, detail="Not enough space")

	db_write = crud.create_file(db, fs_size, file.filename, None) #TODO: Ownership
	if not db_write:
		raise HTTPException(status_code=500, detail="Unknown error")

	with open(join(OS_DIR, db_write.id), "wb") as f:
		file.write(fs)

	return {
		"message": "OK", 
		"id": db_write.id
	}

@app.get("/{item_id}")
async def read(item_id: int, db: Session = Depends(get_db)):
	db_del = crud.get_file(db, item_id)
	if not db_del:
		raise HTTPException(status_code=404, detail="File not found")

	#TODO: Check file owner permission

	return FileResponse(join(OS_DIR, item_id))

@app.patch("/{item_id}")
async def update(item_id: int, file: UploadFile, db: Session = Depends(get_db)):
	db_upd = crud.get_file(db, item_id)
	if not db_upd:
		raise HTTPException(status_code=404, detail="File not found")

	#TODO: Limit size to prevent exploitation
	fs = await file.read()
	fs_size = len(fs)

	#TODO: Check user space available
	#if (crud.get_user_usage(db, None) > 500):
	#	raise HTTPException(status_code=413, detail="Not enough space")

	#TODO: Check file owner permission

	with open(join(OS_DIR, db_upd.id), "wb") as f:
		file.write(fs)

	return {
		"message": "OK"
	}

@app.delete("/{item_id}")
async def delete(item_id: int, db: Session = Depends(get_db)):
	#TODO: Check file owner permission
	db_del = crud.delete_file(db, item_id)
	if not db_del:
		raise HTTPException(status_code=404, detail="File not found")

	return {
		"message": "OK"
	}
