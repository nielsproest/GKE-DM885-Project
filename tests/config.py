import pytest, requests

#Admin user
username = "admin"
password = "password"

#Endpoints
auth_url = "http://34.141.231.32/api/auth"
fs_url = "http://34.141.231.32/api/fs"
job_url = "http://34.141.231.32/api/jobs"
solver_url = "http://34.141.231.32/api/solver"

@pytest.fixture
def get_token():
	with requests.post(auth_url + "/users/login", json={
		"username": username,
		"password": password
		}) as r:
		return r.json()["token"]
