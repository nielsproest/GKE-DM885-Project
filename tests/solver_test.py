import pytest, httpx, requests
from config import *

test_user = "test123"
test_pass = "above_8_chars"

#admin_bearer = get_token()
solverId: str

def setSolderId():
	solvers = requests.get(url=solver_url, headers={"Authorization": f"Bearer {get_token()}"})
	solverId = solvers.json()
	print(solverId)

@pytest.fixture
def test_get_all_solvers():
	with httpx.Client() as client:
		response = client.post(
			solver_url + "/solver",
			headers={"Authorization": f"Bearer {get_token()}"}
		)
		assert response.status_code == 200
		assert response.json()["detail"] == "Success"

@pytest.fixture
def test_get_solver():
	with httpx.Client() as client:
		response = client.post(
			solver_url + f"/solver/{solverId}",
			headers={"Authorization": f"Bearer {get_token()}"}
		)
		assert response.status_code == 200
		assert response.json()["detail"] == "Success"

@pytest.fixture
def test_post_solver():
	with httpx.Client() as client:
		response = client.post(
			solver_url + "/solver/{testName}",
			headers={"Authorization": f"Bearer {get_token()}"},
			json={"image": "minizinc/mznc2019"}
		)
		assert response.status_code == 200
		assert response.json()["detail"] == "Success"

@pytest.fixture
def test_delete_solver():
	with httpx.Client() as client:
		response = client.post(
			solver_url + f"/solver/{solverId}",
			headers={"Authorization": f"Bearer {get_token()}"}
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"


