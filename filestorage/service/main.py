import os,uvicorn

HOST = os.getenv("_HOST", "0.0.0.0:9090").split(":")
DEBUG = os.getenv("_DEBUG", "False") == "True"

if __name__ == "__main__":
	uvicorn.run("app.main:app", host=HOST[0], port=int(HOST[1]), reload=DEBUG)
