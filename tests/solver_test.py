import pytest, httpx, requests
from config import *

test_user = "test123"
test_pass = "above_8_chars"

admin_bearer = '''eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHBpcmF0aW9uIjoiMTY3MTU0OTYyMS42MTQ1ODgiLCJwZXJtaXNzaW9ucyI6eyJpc19hZG1pbiI6dHJ1ZSwidmNwdSI6NjAwLCJyYW0iOjIwNDgsInN0b3JhZ2VfbGltaXQiOjEwNDg1NzYwLCJtYXhfY3B1IjoiMjAwMCIsIm1heF9yYW0iOiIyMDQ4In0sInV1aWQiOiI4ZmMyZmM2My1iN2JhLTRmOGYtYmNhMy0zZjNkNGVmYWJiNjUifQ.RljmYY3rQ9aSllyKSPGjubKdWYy7cwa37kV9u0xgLNxDQYyV06FKDIzE_vC44HzoA_cMVK-e4ZrUWL3oA7nTUoe7hK5nXGIHPt0ix8iZzdA0KiP-qm3X3JE1drhnUbTnY5tBEY-zYisOm_s_byx6aEQ0N5GUkyWVDrm_B8Xe8qI-R-ZbOjPNxoO03M4pVmQfVxz7x7RtqSGKx9tJQKLDLv-UxRQhhdFUeFOFjgjcYPw0TnjiomZO-sG4Tp2rvO7YKfZikqjGsKokymR6JtxH-0G6q7HRpbuMr64swh3ToJP3iRJGEsUtvExFOoHFOsZS-6Jm5MmhtPOa9hlh_HAzTw'''

@pytest.fixture
def getSolverId(get_token):
	solvers = requests.get(url=solver_url+"/solver", headers={"Authorization": f"Bearer {get_token}"})
	for solver in solvers.json():
		if solver["name"] == "sunny-cp":
			return solver["id"]

@pytest.fixture
def delSolverId(get_token):
	solvers = requests.get(url=solver_url+"/solver", headers={"Authorization": f"Bearer {get_token}"})
	for solver in solvers.json():
		if solver["name"] == "{testName}":
			return solver["id"]

def test_get_all_solvers(get_token):
	with httpx.Client() as client:
		response = client.get(
			solver_url + "/solver",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200

def test_get_solver(get_token, getSolverId):
	with httpx.Client() as client:
		response = client.get(
			solver_url + f"/solver/{getSolverId}",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200

def test_post_solver(get_token):
	with httpx.Client() as client:
		response = client.post(
			solver_url + "/solver/{testName}",
			headers={"Authorization": f"Bearer {get_token}"},
			json={"image": "minizinc/mznc2019"}
		)
		assert response.status_code == 200

def test_delete_solver(get_token, delSolverId):
	with httpx.Client() as client:
		response = client.delete(
			solver_url + f"/solver/{delSolverId}",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200