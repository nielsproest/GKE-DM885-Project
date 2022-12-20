import pytest, requests

#Admin user
username = "admin"
password = "password"

#Endpoints
service_url = "http://35.204.110.143"
auth_url = f"{service_url}/api/auth"
fs_url = f"{service_url}/api/fs"
job_url = f"{service_url}/api/jobs"
solver_url = f"{service_url}/api/solver"

@pytest.fixture
def get_token():
	with requests.post(auth_url + "/users/login", json={
		"username": username,
		"password": password
		}) as r:
		return r.json()["token"]
