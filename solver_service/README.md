## Start up locally:

### Install dependencies:

pip install -r requirements.txt
pip install "uvicorn[standard]"

### Create database:

(in /solver_service/db)
sudo docker build . -t solver_service_db
sudo docker run -e POSTGRES_PASSWORD=password -p 5432:5432 solver_service_db

### Start web server:

(from solver_service/app folder)
uvicorn main:app --reload

Access it at 127.0.0.1:8000.

## Start up on minikube:

