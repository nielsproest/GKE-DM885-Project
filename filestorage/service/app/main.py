from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from os.path import join
from os import remove, getenv, mkdir
from re import sub
from pydantic import BaseModel

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
OS_DIR = getenv("_STORAGE_DIR", "/mnt/hdd/dumbaf")

try:
	mkdir(OS_DIR)
except:
	print("Failed to create directory!")

def generic_auth_handler(user_id, token):
	decoded_token = decode_jwt(token)
	permissions = decoded_token.get("permissions", None)

	if permissions is None:
		raise HTTPException(
			status_code=400, detail="Missing permissions"
		)

	if not permissions["is_admin"] and user_id != decoded_token["uuid"]:
		raise HTTPException(
			status_code=401, detail="Wrong user for said resource"
		)

	return permissions

def sanitize(s):
	return sub(r'[^A-Za-z0-9 ]+ _.-' , '', s)

class Message(BaseModel):
	message: str

class MessageWithid(Message):
	id: int

@app.put("/{user_id}", 
	response_model=MessageWithid,
	responses={
		413: {
			"description": "Not enough space available"
		},
		500: {
			"description": "Server error when creating file"
		},
		200: {
			"content": {
				"application/json": {
					"message": "OK",
					"id": "file_id"
				}
			}
		}
	}
)
async def write(
		user_id: str,
		file: UploadFile,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer()),
	):
	"""
		Writes a file as given user_id
		Returns the file id.
		Requires authorization as given user or admin 
		(in the form of HTTP Header Authorization: Bearer INSERT_TOKEN)
	"""
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
	qry = crud.create_file(db, sanitize(file.filename), fs_size, user_id)
	if not qry:
		raise HTTPException(status_code=500, detail="Unknown error")

	#Write file
	with open(join(OS_DIR, str(qry.id)), "wb") as f:
		f.write(fs)

	return {
		"message": "OK",
		"id": qry.id
	}


class ItemList(BaseModel):
	id: int
	name: str
	owner: str
	size: int
	class Config:
		orm_mode = True

class MessageWithList(Message):
	lst: list[ItemList]
	class Config:
		orm_mode = True

@app.get("/{user_id}/list", 
	response_model=MessageWithList,
	responses={
		200: {
			"content": {
				"application/json": {
					"message": "OK",
					"lst": [{
						"id": 0,
						"name": "example.txt",
						"owner": "1234-5678-9101-1121",
						"size": 10,
					}]
				}
			}
		}
	}
)
async def lst(
		user_id: str,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	"""
		Lists a given user's files
		Requires authorization as given user or admin
	"""
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_user_files(db, user_id)
	if not qry:
		qry = []

	return {
		"message": "OK",
		"lst": qry
	}

@app.delete("/{user_id}/delete", 
	response_model=Message,
	responses={
		200: {
			"content": {
				"application/json": {
					"message": "OK",
				}
			}
		}
	}
)
async def delete_all(
		user_id: str,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	"""
		Deletes all a users files
		Requires authorization as given user or admin
	"""
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_user_files(db, user_id)
	if not qry:
		return {
			"message": "OK"
		}

	for i in qry:
		try:
			remove(join(OS_DIR, str(i.id)))
		except:
			print("File not found ", i)

	crud.delete_user_files(db, user_id)

	return {
		"message": "OK"
	}

class Item(BaseModel):
	id: str
	value: str
@app.get("/{user_id}/{item_id}", 
	response_model=Item,
	responses={
		200: {
			"content": {"text/plain": {}},
			"description": "Return the file.",
		},
		410: {
			"description": "File not found.",
		}
	}
)
async def read(
		user_id: str,
		item_id: int,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	"""
		Returns a file from a user
		Requires authorization as given user or admin
	"""
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=410, detail="File not found")

	return FileResponse(join(OS_DIR, str(item_id)), filename=qry.name)

@app.patch("/{user_id}/{item_id}", 
	response_model=Message,
	responses={
		200: {
			"content": {
				"application/json": {
					"message": "OK",
				}
			}
		},
		410: {
			"description": "File not found.",
		},
		413: {
			"description": "Not enough space available"
		},
	}
)
async def update(
		user_id: str,
		item_id: int,
		file: UploadFile,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	"""
		Updates a user's file
		Requires authorization as given user or admin
	"""
	permissions = generic_auth_handler(user_id, token)

	qry = crud.get_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=410, detail="File not found")

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

	crud.update_file(db, item_id, sanitize(file.filename), fs_size)

	return {
		"message": "OK"
	}

@app.delete("/{user_id}/{item_id}", 
	response_model=Message,
	responses={
		200: {
			"content": {
				"application/json": {
					"message": "OK",
				}
			}
		},
		410: {
			"description": "File not found.",
		},
	}
)
async def delete(
		user_id: str,
		item_id: int,
		db: Session = Depends(get_db),
		token=Depends(JWTBearer())
	):
	"""
		Deletes a user's file
		Requires authorization as given user or admin
	"""
	permissions = generic_auth_handler(user_id, token)

	qry = crud.delete_file(db, item_id)
	if not qry:
		raise HTTPException(status_code=410, detail="File not found")

	remove(join(OS_DIR, str(item_id)))

	return {
		"message": "OK"
	}
