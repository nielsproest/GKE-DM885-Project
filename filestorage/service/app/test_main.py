from fastapi.testclient import TestClient

from .main import app
import requests, pytest

client = TestClient(app)

def getToken():
	with requests.post("http://127.0.0.1:5000/users/login", json={
		"username": "admin",
		"password": "password"
		}) as r:
		return r.json()["token"]

def test_create_file():
	app.token = getToken()
	app.fileid = 0

	t_file = "test.csv"
	t_str = "The test string should be unique"

	response = client.put(
		"/test",
		headers={"Authorization": f"Bearer {app.token}"},
		files={"file": (t_file, t_str)},
	)
	assert response.status_code == 200
	assert response.json()["message"] == "OK"
	app.fileid = response.json()["id"]

def test_list_files():
	response = client.get(
		"/test/list",
		headers={"Authorization": f"Bearer {app.token}"}
	)
	assert response.status_code == 200
	assert response.json()["message"] == "OK"
	assert len([i["id"] == app.fileid for i in response.json()["lst"]]) > 0

def test_read():
	t_file = "test.csv"
	t_str = "The test string should be unique"

	response = client.get(
		f"/test/{app.fileid}",
		headers={"Authorization": f"Bearer {app.token}"}
	)
	assert response.status_code == 200
	assert response.content == t_str.encode('ascii')

def test_patch():
	t_file = "test2.csv"
	t_str = "The test string should be different"

	response = client.patch(
		f"/test/{app.fileid}",
		headers={"Authorization": f"Bearer {app.token}"},
		files={"file": (t_file, t_str)},
	)
	assert response.status_code == 200

def test_read_patch():
	t_file = "test2.csv"
	t_str = "The test string should be different"

	response = client.get(
		f"/test/{app.fileid}",
		headers={"Authorization": f"Bearer {app.token}"}
	)
	assert response.status_code == 200
	assert response.content == t_str.encode('ascii')

def test_delete():
	response = client.delete(
		f"/test/{app.fileid}",
		headers={"Authorization": f"Bearer {app.token}"}
	)
	assert response.status_code == 200

#def test_mass_delete():
#	response = client.delete(
#		f"/test/delete",
#		headers={"Authorization": f"Bearer {app.token}"}
#	)
#	assert response.status_code == 200
