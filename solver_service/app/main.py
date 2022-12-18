from fastapi import FastAPI, Depends, HTTPException
import uuid
import os
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from models import Solver
from crud import cGetAllSolvers, cPostSolver, cDeleteSolver, cGetSolver
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

app = FastAPI()

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
    #Name and solver url for solvers to be added on startup if they do not exist
    permSolvers = {"fzn-picat-sat": "hakankj/fzn-picat-sat", "geas": "gkgange/geas-mznc2022"}

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
def postSolver(name: str, image: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    isAdmin(token)
    isInDb(db, image)
    #verify_image(image)

    cPostSolver(db, name, image)

    return {"success"}

def isValidUuid(solverId):
    try:
        uuid.UUID(str(solverId))
        return
    except ValueError:
        raise HTTPException(status_code=400, detail="Id not valid")


def verify_image(dockerImage: str):
    #Currently verifies by pulling the image - checking all tags, which is either successful or returns an error if image does not exist
    #TODO: Use docker hub api to check images instead

    return

def isAdmin(token: str):
    admin = decode_jwt(token).get('permissions').get('is_admin')
    if not admin:
        raise HTTPException(status_code=401, detail="User is not admin")

def isInDb(db: Session, image: str):
    solvers = getAllSolvers(db)
    solverURLs = []

    for solver in solvers:
        solverURLs.append(solver.dockerImage)

    if image in solverURLs:
        raise HTTPException(status_code=409, detail="Image already exists in database")

def startupDbPrep(permSolvers: dict):
    db = SessionLocal()
    solvers = getAllSolvers(db)

    solverURLs = []

    for solver in solvers:
        solverURLs.append(solver.dockerImage)

    for perm in permSolvers:
        if not permSolvers.get(perm) in solverURLs:
            cPostSolver(db, perm, permSolvers.get(perm))

def startupPkPrep():

    if os.getenv('KUBERNETES_SERVICE_HOST'):
        r = requests.get(url = auth_url + "/keys/public_key")
        data = r.json()
        setPublicKey(data["message"])
    else:
        setPublicKey('''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvpAXDxizoN4MHs0qJrQ9J/Dc+95mLbT7o/haw2vXuB2LoSp855W/5hpPqyhAkPmKJEzICp6Ke72a2oUVeJb8lckM3km9dxFBvNsbMEpKEOO1/WhmWw8aDwBI7E0s7KAXHSdqCBncB4L3W37O9c6bQ2QrGpfrN82yFXez25tdv1ODc7bzfYFdD5LHNVymYl0E+dR/4P2P/+YxUX7omUI9Bqt6jdw6uERt2tcyT0PFT2DQwf3mtrXCufo68uMfxKP0TN5c1Zan4jwXeiJE4wHPzFgaWTzgKB6xayJqkgI9nhy5KaONIKe+ZCerrsBKztk9R8uH38GdI2rcwCPYi2AkkQIDAQAB
-----END PUBLIC KEY-----''')
