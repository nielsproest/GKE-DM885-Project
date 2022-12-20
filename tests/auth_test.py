import pytest, httpx, random
from config import *

@pytest.fixture
def test_create_user():
	c_user = "test" + str(random.randrange(0,10000))
	c_pass = "above_8_chars"

	with httpx.Client() as client:
		response = client.post(
			auth_url + "/users/signup",
			json={"username": c_user, "password": c_pass}
		)
		assert response.status_code == 200
		assert "token" in response.json()

		response = client.post(
			auth_url + "/users/login",
			json={"username": c_user, "password": c_pass}
		)
		assert response.status_code == 200
		return response.json()["token"]

@pytest.fixture
def test_get_user_uuid(test_create_user):
	with httpx.Client() as client:
		response = client.get(
			auth_url + "/users/get_my_permissions",
			headers={"Authorization": f"Bearer {test_create_user}"}
		)
		assert response.status_code == 200
		return response.json()["message"]["uuid"]

@pytest.fixture
def test_modify_user_permissions(get_token, test_get_user_uuid):
	with httpx.Client() as client:
		response = client.post(
			auth_url + "/users/modify",
			json={
				"uuid": test_get_user_uuid,
				"data": {
					"ram": 2048,
					"vcpu": 600,
					"is_admin": True
				}
			},
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200

def test_get_user_permissions(test_create_user, test_modify_user_permissions):
	with httpx.Client() as client:
		response = client.get(
			auth_url + "/users/get_my_permissions",
			headers={"Authorization": f"Bearer {test_create_user}"}
		)
		assert response.status_code == 200
		assert response.json()["message"]["is_admin"] == True

def test_delete_user(get_token, test_get_user_uuid):
	with httpx.Client() as client:
		response = client.post(
			auth_url + "/users/delete",
			json={
				"uuid": test_get_user_uuid,
			},
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200
