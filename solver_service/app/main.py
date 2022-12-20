from fastapi import FastAPI, Depends, HTTPException, Body
import uuid
import os
import requests
from urllib.parse import unquote
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from models import Solver
from crud import cGetAllSolvers, cPostSolver, cDeleteSolver, cGetSolver, cGetSolverByImage
from database import engine, SessionLocal
from auth_handler import JWTBearer
from auth import setPublicKey, decode_jwt

Solver.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(root_path="/api/solver" if os.getenv('KUBERNETES_SERVICE_HOST') else "")

# CHANGE FOR PRODUCTION
origins = [
    "http://localhost",
    "http://localhost:3000",
]

# Adding cors rules
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_url = "http://auth-service.default.svc.cluster.local:5000"

@app.on_event("startup")
async def startup_event():
    #Name and solver url for solvers to be added on startup if they do not exist - VVV
    permSolvers = {"fzn-picat-sat": "hakankj/fzn-picat-sat", "geas": "gkgange/geas-mznc2022", "sunny-cp": "jacopomauro/sunny-cp"}

    startupDbPrep(permSolvers)
    startupPkPrep()

@app.get("/solver", dependencies=[Depends(JWTBearer())])
def getAllSolvers(db: Session = Depends(get_db)):

    return cGetAllSolvers(db)

@app.get("/solver/{solverId}", dependencies=[Depends(JWTBearer())])
def getSolver(solverId: str, db: Session = Depends(get_db)):

    isValidUuid(solverId)

    return cGetSolver(db, solverId)

@app.delete("/solver/{solverId}", dependencies=[Depends(JWTBearer())])
def deleteSolver(solverId: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    isAdmin(token)
    isValidUuid(solverId)

    cDeleteSolver(db, solverId)

    return {"success"}

@app.post("/solver/{name}", dependencies=[Depends(JWTBearer())])
def postSolver(name: str, payload=Body({"image": "some-image-here"}), db: Session = Depends(get_db), token=Depends(JWTBearer())):
    
    image = payload.get("image", None)

    isAdmin(token)
    isInDb(db, image)
    
    response = verify_image(image)
    
    cPostSolver(db, name, image)

    return {response}

def isValidUuid(solverId):
    try:
        uuid.UUID(str(solverId))
        return
    except ValueError:
        raise HTTPException(status_code=400, detail="Id not valid")


def verify_image(image: str) -> str:
    namespace: str
    repository: str
    splitString: list
    status: int

    try:
        req = requests.get(image, timeout=5)
        if req.status_code is None:
            status = 400
        else:
            status = req.status_code    
    except:
        status = 400

    #Is a docker hub URL
    if "hub.docker.com/r/" in image:
        splitString = image.index("/r/")
        image = image[splitString + 3:]
        #Get name space and repository if it is a valid docker image - which requires excatly one /
        if "/" in image:
            splitString = image.split("/")
            namespace = splitString[0]
            repository = splitString[1]
        else: 
            raise HTTPException(status_code=400, detail="Not a valid docker hub image")
        #Attempts to check tags of the docker image
        r = requests.get(f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Docker image not found")
        return "success"
    #Is not accessable URL, might still be docker image on docker hub    
    elif "/" in image and status == 400:
        splitString = image.split("/")
        namespace = splitString[0]
        repository = splitString[1]
        r = requests.get(f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags")
        if r.status_code == 200:
            return "success"
        elif r.status_code == 404:
            raise HTTPException(status_code=404, detail="Docker image not found")
    #Is URL not leading to docker hub, images from here may or may not work
    else:
        return "not on docker hub"

def isAdmin(token: str):
    admin = decode_jwt(token).get('permissions').get('is_admin')
    if not admin:
        raise HTTPException(status_code=401, detail="User is not admin")

def isInDb(db: Session, image: str):
    if "hub.docker.com/r/" in image:
        splitString = image.index("/r/")
        image = image[splitString + 3:]

    db_solver = cGetSolverByImage(db, image)
    if  db_solver == None:
        return

    db_dockerImage = db_solver.dockerImage

    if image == db_dockerImage:
        raise HTTPException(status_code=409, detail="Image already exists in database")

def startupDbPrep(permSolvers: dict):
    db = SessionLocal()

    for perm in permSolvers:
        tempSolver = cGetSolverByImage(db, permSolvers.get(perm))
        if tempSolver == None:
            cPostSolver(db, perm, permSolvers.get(perm))

def startupPkPrep():

    if os.getenv('KUBERNETES_SERVICE_HOST'):
        r = requests.get(url = auth_url + "/keys/public_key")
        data = r.json()
        setPublicKey(data["message"])
    else:
        print("Could not get public key")
