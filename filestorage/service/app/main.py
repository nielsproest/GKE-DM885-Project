from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from os.path import join
from os import remove, getenv

#TODO: Pydantic Schemas for returning data consistently
from . import crud, models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#TODO: Get running by monday

# Dependency
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

#Where our files are stored
OS_DIR = getenv("_STORAGE_DIR", "/mnt/hdd")

a_hundred_mb = 1024*1024*100

@app.put("/{user_id}/")
async def write(user_id: str, file: UploadFile, db: Session = Depends(get_db)):
	#TODO: Check user auth

	#TODO: Limit size to prevent exploitation
	#TODO: Move to file write (dont keep in memory), and update size after (TODO: Is it unsafe?)
	fs = await file.read()
	fs_size = len(fs)

	#Check user space available
	usage = crud.get_user_usage(db, user_id)
	if (usage != None and usage + fs_size > a_hundred_mb):
		raise HTTPException(status_code=413, detail="Not enough space")

	#Create file
	qry = crud.create_file(db, file.filename, fs_size, user_id) #TODO: Ownership
	if not qry:
		raise HTTPException(status_code=500, detail="Unknown error")

	#Write file
	with open(join(OS_DIR, str(qry.id)), "wb") as f:
		f.write(fs)

	return {
		"message": "OK", 
		"id": qry.id
	}

@app.get("/{user_id}/list")
async def lst(user_id: str, db: Session = Depends(get_db)):
	#TODO: Check user auth
	qry = crud.get_files(db, user_id)
	if not qry:
		raise HTTPException(status_code=404, detail="No files available")

	return {
		"message": "OK", 
		"lst": qry
	}

@app.get("/{user_id}/{item_id}")
async def read(user_id: str, item_id: int, db: Session = Depends(get_db)):
	#TODO: Check user auth
	qry = crud.get_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=404, detail="File not found")

	return FileResponse(join(OS_DIR, str(item_id)), filename=qry.name)

@app.patch("/{user_id}/{item_id}")
async def update(user_id: str, item_id: int, file: UploadFile, db: Session = Depends(get_db)):
	#TODO: Check user auth
	qry = crud.get_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=404, detail="File not found")

	#TODO: Limit size to prevent exploitation
	fs = await file.read()
	fs_size = len(fs)

	#Check user space available
	usage = crud.get_user_usage(db, user_id)
	if (usage != None and usage + fs_size > a_hundred_mb):
		raise HTTPException(status_code=413, detail="Not enough space")

	with open(join(OS_DIR, str(qry.id)), "wb") as f:
		f.write(fs)

	return {
		"message": "OK"
	}

@app.delete("/{user_id}/{item_id}")
async def delete(user_id: str, item_id: int, db: Session = Depends(get_db)):
	#TODO: Check user auth
	qry = crud.delete_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=404, detail="File not found")

	remove(join(OS_DIR, str(item_id)))

	return {
		"message": "OK"
	}
