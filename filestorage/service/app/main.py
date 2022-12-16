from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from os.path import join
from os import remove, getenv, mkdir

from . import crud, models
from .database import SessionLocal, engine
from .auth import JWTBearer, decode_jwt

models.Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api/fs" if getenv('KUBERNETES_SERVICE_HOST') else "")

# Dependency
def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

#Where our files are stored
OS_DIR = getenv("_STORAGE_DIR", "/mnt/hdd")

try:
	mkdir(OS_DIR)
except:
	print("Failed to create directory!")

def generic_auth_handler(user_id, token):
	permissions = decode_jwt(token).get("permissions", None)

	if permissions is None:
		raise HTTPException(
			status_code=400, detail="Missing permissions"
		)

	if not permissions["is_admin"] and user_id != permissions["uuid"]:
		raise HTTPException(
			status_code=401, detail="Wrong user for said resource"
		)

	return permissions

@app.put("/{user_id}")
async def write(
		user_id: str,
		file: UploadFile,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	permissions = generic_auth_handler(user_id, token)

	#The load balancer is expected to limit size, so this isnt an exploit
	fs = await file.read()
	fs_size = len(fs)

	#Check user space available
	usage = crud.get_user_usage(db, user_id)
	allowed_usage = permissions["storage_limit"]
	if (usage != None and not permissions["is_admin"] and usage + fs_size > allowed_usage):
		raise HTTPException(status_code=413, detail="Not enough space")

	#Create file
	qry = crud.create_file(db, file.filename, fs_size, user_id)
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
async def lst(
		user_id: str,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_files(db, user_id)
	if not qry:
		raise HTTPException(status_code=404, detail="No files available")

	return {
		"message": "OK",
		"lst": qry
	}

@app.get("/{user_id}/{item_id}")
async def read(
		user_id: str,
		item_id: int,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=404, detail="File not found")

	return FileResponse(join(OS_DIR, str(item_id)), filename=qry.name)

@app.patch("/{user_id}/{item_id}")
async def update(
		user_id: str,
		item_id: int,
		file: UploadFile,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=404, detail="File not found")

	#The load balancer is expected to limit size, so this isnt an exploit
	fs = await file.read()
	fs_size = len(fs)

	#Check user space available
	usage = crud.get_user_usage(db, user_id)
	allowed_usage = permissions["storage_limit"]
	if (usage != None and not permissions["is_admin"] and usage + fs_size > allowed_usage):
		raise HTTPException(status_code=413, detail="Not enough space")

	with open(join(OS_DIR, str(qry.id)), "wb") as f:
		f.write(fs)

	return {
		"message": "OK"
	}

@app.delete("/{user_id}/{item_id}")
async def delete(
		user_id: str,
		item_id: int,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	permissions = generic_auth_handler(user_id, token)

	qry = crud.delete_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=404, detail="File not found")

	remove(join(OS_DIR, str(item_id)))

	return {
		"message": "OK"
	}

@app.delete("/{user_id}/delete")
async def delete(
		user_id: str,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_files(db, user_id)
	if not qry:
		raise HTTPException(status_code=404, detail="Files not found")

	for i in qry:
		try:
			remove(join(OS_DIR, str(i.id)))
		except:
			print("File not found ", i)

	return {
		"message": "OK"
	}
