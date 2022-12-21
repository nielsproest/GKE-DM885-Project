from fastapi import FastAPI, Depends, HTTPException, Body
import uuid, os,requests
from pydantic import BaseModel
from urllib.parse import unquote
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from schemas import SolverSchema
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


class Detail(BaseModel):
    detail: str = "error message"

class Success(BaseModel):
    success: str = "success message"

'''
Returns all solvers in the database
'''
@app.get("/solver", dependencies=[Depends(JWTBearer())], responses={
    200: {"model": List[SolverSchema], "description": "All solvers in database returned"}
})
def Get_All_Solvers(db: Session = Depends(get_db)):

    return cGetAllSolvers(db)

'''
Returns a solver with the given solverId if it exist
'''
@app.get("/solver/{solverId}", dependencies=[Depends(JWTBearer())], responses={
    200: {"model": SolverSchema, "description": "All solvers in database returned"},
    400: {"model": Detail, "description": "Id not valid"},
    404: {"model": Detail, "description": "Solver id not found"}
})
def Get_Solver(solverId: str, db: Session = Depends(get_db)):

    isValidUuid(solverId)
    solver = cGetSolver(db, solverId)
    if solver is None:
        raise HTTPException(status_code=404, detail="Solver id not found")
    return solver

'''
Deletes the solver with the given solverId if it exists
'''
@app.delete("/solver/{solverId}", dependencies=[Depends(JWTBearer())], responses={
    200: {"model": Success, "description": "Success"},
    400: {"model": Detail, "description": "Id not valid"},
    401: {"model": Detail, "description": "User is not admin"},
    404: {"model": Detail, "description": "Solver id not found"}
})
def Delete_Solver(solverId: str, db: Session = Depends(get_db), token=Depends(JWTBearer())):

    isAdmin(token)
    isValidUuid(solverId)

    solver = cDeleteSolver(db, solverId)
    if solver is None:
        raise HTTPException(status_code=404, detail="Solver id not found")
    return {"detail": "Success"}

'''
Adds a given solver URL to the database with the given name
'''
@app.post("/solver/{name}", dependencies=[Depends(JWTBearer())], responses={
                    200: {"description": "Success", "content": {"application/json": {"examples": {
                    "success": {"summary": "Success", "value": {"message": "Success"}},
                    "not on docker": {"summary": "Not on docker hub", "value": {"message": "Not on docker hub"}}}}}},
                    400: {"model": Detail, "description": "Not a valid docker hub image"},
                    401: {"model": Detail, "description": "User is not admin"},
                    404: {"description": "Image or solver id not found", "content": {"application/json": {"examples": {
                    "docker image": {"summary": "Docker image not found", "value": {"message": "Docker image not found"}},
                    "solver id": {"summary": "Solver id not found", "value": {"message": "Solver id not found"}}}}}},
                    409: {"model": Detail, "description": "Image already exists in database"}
                    })
def Post_Solver(name: str, payload=Body({"image": "some-image-here"}), db: Session = Depends(get_db), token=Depends(JWTBearer())):
    
    image = payload.get("image", None)

    isAdmin(token)
    isInDb(db, image)
    
    response = verify_image(image)
    
    solver = cPostSolver(db, name, image)
    if solver is None:
        raise HTTPException(status_code=404, detail="Solver id not found")

    return {"detail": response}

'''
Checks if a given id is a valid UUID
'''
def isValidUuid(solverId):
    try:
        uuid.UUID(str(solverId))
        return
    except ValueError:
        raise HTTPException(status_code=400, detail="Id not valid")

'''
Returns "success" if a given URL exist on docker hub as a valid image Or "not on docker hub" if it does not
'''
def verify_image(image: str) -> str:
    namespace: str
    repository: str
    splitString: list

    #Is a docker hub URL
    if "hub.docker.com/r/" in image:
        splitString = image.index("/r/")
        image = image[splitString + 3:]
        #Get name space and repository if it is a valid docker image - which requires excatly one /
        if "/" in image:
            splitString = image.split("/")
            if len(splitString) == 2:
                namespace = splitString[0]
                repository = splitString[1]
            else: 
                raise HTTPException(status_code=400, detail="Not a valid docker hub image")
        #Attempts to check tags of the docker image
        r = requests.get(f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Docker image not found")
        return "Success"
    #Is not an URL, might still be docker image on docker hub    
    elif "/" in image and status(image) == 400:
        splitString = image.split("/")
        if len(splitString) == 2:
            namespace = splitString[0]
            repository = splitString[1]
        else:
            raise HTTPException(status_code=400, detail="Not a valid docker hub image")
        r = requests.get(f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{repository}/tags")
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Docker image not found")
        return "Success"
    #Is URL not leading to docker hub, images from here may or may not work
    else:
        return "Not on docker hub"

'''
Returns status of url if it exists
'''
def status(image: str) -> int:
    try:
        req = requests.get(image, timeout=10)
        if req.status_code is None:
            return 400
        else:
            return req.status_code    
    except:
        return 400

'''
Checks if user is admin
'''
def isAdmin(token: str):
    admin = decode_jwt(token).get('permissions').get('is_admin')
    if not admin:
        raise HTTPException(status_code=401, detail="User is not admin")

'''
Checks if image already exists in the database
'''
def isInDb(db: Session, image: str):
    if "hub.docker.com/r/" in image:
        splitString = image.index("/r/")
        image = image[splitString + 3:]

    db_solver = cGetSolverByImage(db, image)
    #Image does not exist
    if  db_solver == None:
        return 

    if image == db_solver.dockerImage:
        raise HTTPException(status_code=409, detail="Image already exists in database")

'''
Adds solvers on startup to the database
'''
def startupDbPrep(permSolvers: dict):
    db = SessionLocal()

    for perm in permSolvers:
        tempSolver = cGetSolverByImage(db, permSolvers.get(perm))
        if tempSolver == None:
            cPostSolver(db, perm, permSolvers.get(perm))

'''
Gets and sets public key needed for authentication
'''
def startupPkPrep():

    if os.getenv('KUBERNETES_SERVICE_HOST'):
        r = requests.get(url = auth_url + "/keys/public_key")
        data = r.json()
        setPublicKey(data["message"])
    else:
        print("Could not get public key")
