import pytest, httpx
from config import *

@pytest.fixture
def test_create_file(get_token):
	t_file = "test.csv"
	t_str = "The test string should be unique"

	with httpx.Client() as client:
		response = client.put(
			fs_url + "/test",
			headers={"Authorization": f"Bearer {get_token}"},
			files={"file": (t_file, t_str)},
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"
		return response.json()["id"]

def test_list_files(get_token, test_create_file):
	with httpx.Client() as client:
		response = client.get(
			fs_url + "/test/list",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"
		assert len([i["id"] == test_create_file for i in response.json()["lst"]]) > 0

def test_read(get_token, test_create_file):
	t_file = "test.csv"
	t_str = "The test string should be unique"

	with httpx.Client() as client:
		response = client.get(
			f"{fs_url}/test/{test_create_file}",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200
		assert response.content == t_str.encode('ascii')

@pytest.fixture
def test_patch(get_token, test_create_file):
	t_file = "test2.csv"
	t_str = "The test string should be different"

	with httpx.Client() as client:
		response = client.patch(
			f"{fs_url}/test/{test_create_file}",
			headers={"Authorization": f"Bearer {get_token}"},
			files={"file": (t_file, t_str)},
		)
		assert response.status_code == 200

@pytest.fixture
def test_read_patch(get_token, test_create_file, test_patch):
	t_file = "test2.csv"
	t_str = "The test string should be different"

	with httpx.Client() as client:
		response = client.get(
			f"{fs_url}/test/{test_create_file}",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200
		assert response.content == t_str.encode('ascii')

@pytest.fixture
def test_delete(get_token, test_create_file, test_read_patch):
	with httpx.Client() as client:
		response = client.delete(
			f"{fs_url}/test/{test_create_file}",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200

def test_mass_delete(get_token, test_delete):
	t_file = "test.csv"
	t_str = "The test string should be unique"

	with httpx.Client() as client:
		response = client.put(
			f"{fs_url}/test",
			headers={"Authorization": f"Bearer {get_token}"},
			files={"file": (t_file, t_str)},
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"

		response = client.delete(
			f"{fs_url}/test/delete",
			headers={"Authorization": f"Bearer {get_token}"},
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"

		response = client.get(
			fs_url + "/test/list",
			headers={"Authorization": f"Bearer {get_token}"}
		)
		assert response.status_code == 200
		assert response.json()["message"] == "OK"
		assert len(response.json()["lst"]) == 0
