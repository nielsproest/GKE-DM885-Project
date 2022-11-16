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


@app.put("/")
async def write(file: UploadFile, db: Session = Depends(get_db)):
	db_write = crud.create_file(db, file.filename, None) #TODO: Ownership
	if not db_write:
		raise HTTPException(status_code=500, detail="Unknown error")

	with open(join(OS_DIR, db_write.id), "wb") as f:
		file.write(f)

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

@app.delete("/{item_id}")
async def delete(item_id: int, db: Session = Depends(get_db)):
	db_del = crud.delete_file(db, item_id)
	if not db_del:
		raise HTTPException(status_code=404, detail="File not found")

	return {
		"message": "OK"
	}
