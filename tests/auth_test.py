import requests, pytest, httpx
from config import *

test_user = "test123"
test_pass = "above_8_chars"

@pytest.fixture
def get_token():
	with requests.post(auth_url + "/users/login", json={
		"username": "admin",
		"password": "password"
		}) as r:
		return r.json()["token"]

@pytest.fixture
def test_create_user():
	with httpx.Client() as client:
		response = client.post(
			auth_url + "/users/signup",
			json={"username": test_user, "password": test_pass}
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"

@pytest.fixture
def test_create_user():
	with httpx.Client() as client:
		response = client.post(
			auth_url + "/users/signup",
			json={"username": test_user, "password": test_pass}
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"
