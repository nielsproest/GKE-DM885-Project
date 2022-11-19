
Install dependencies:

```
pip install fastapi
pip install "uvicorn[standard]"
```

Start db
```
(in /jobservice/db)
sudo docker build -t job_service_db ./
sudo docker run --name job_service_db -d -e POSTGRES_PASSWORD=psltest -p 5432:5432 job_service_db
```


Start web server.

```
uvicorn main:app --reload
```

Access it at localhost:8000.
The localhost:8000/docs endpoint gives a nice way to test the API.









