import requests, pytest, httpx
from config import *

@pytest.fixture
def get_token():
	with requests.post(auth_url + "/users/login", json={
		"username": "admin",
		"password": "password"
		}) as r:
		return r.json()["token"]

