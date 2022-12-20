import pytest, httpx
from config import *

test_user = "test123"
test_pass = "above_8_chars"

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
def test_login_user(test_create_user):
	with httpx.Client() as client:
		response = client.post(
			auth_url + "/users/login",
			json={"username": test_user, "password": test_pass}
		)
		assert response.status_code == 200
		return response.json()["token"]

@pytest.fixture
def test_get_user_permissions(test_login_user):
	with httpx.Client() as client:
		response = client.post(
			auth_url + "/users/get_my_permissions",
			headers={"Authorization": f"Bearer {test_login_user}"}
		)
		assert response.status_code == 200
		print(response.json())

