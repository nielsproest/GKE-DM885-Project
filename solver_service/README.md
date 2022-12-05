# Start up locally;

Install dependencies:

```
pip install -r requirements.txt
pip install "uvicorn[standard]"
```

Start db
```
(in /solver_service/db)
sudo docker build . -t solver_service_db
sudo docker run -e POSTGRES_PASSWORD=password -p 5432:5432 solver_service_db
```

Start web server.

```
(from DM855-Project folder)
uvicorn solver_service.app.main:app --reload
```

Access it at localhost:8000.

# Start up on minikube:

