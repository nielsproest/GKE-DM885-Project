
Install dependencies:

```
pip install fastapi
pip install "uvicorn[standard]"
```


Start web server.

```
uvicorn app.main:app --reload
```

Access it at localhost:8000.
The localhost:8000/docs endpoint gives a nice way to test the API.