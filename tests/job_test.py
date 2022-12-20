import pytest, httpx, random, time
from config import *

@pytest.fixture
def fs_upload_mzn(get_token):
  t_file = "coins.mzn"
  t_str = '''int: amount = 78;
array[1..4] of int: denoms = [25, 10, 5, 1];

array[1..4] of var 0..100: counts;

% ------------------------------------------

constraint sum(i in 1..4) ( counts[i] * denoms[i] ) = amount;

var int: coins = sum(counts);
solve minimize coins;

output [
  "coins = ", show(coins), ";",
  "denoms = ", show(denoms), ";",
  "counts = ", show(counts), ";"
];'''
  print(get_token)
  with httpx.Client() as client:
    response = client.put(
      fs_url + "/test",
      headers={"Authorization": f"Bearer {get_token}"},
      files={"file": (t_file, t_str)},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "OK"
    return response.json()["id"]

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
def test_get_user_uuid(get_token):
  with httpx.Client() as client:
    response = client.get(
      auth_url + "/users/get_my_permissions",
      headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    return response.json()["message"]["uuid"]


def test_start_job(test_create_user, fs_upload_mzn):
  print(test_create_user)
  with httpx.Client() as client:
    token = test_create_user
    response = client.post(
      job_url + "/job",
      headers={"Authorization": f"Bearer {token}"},
      json={
                "mzn_id": fs_upload_mzn,
                "dzn_id": None,
                "timeout": 120,
                "solver_list": [
                  {
                    "id": "a9ad03c4-8621-4e6d-af5f-5cb9f7eef0ff",
                    "name": "solver-1",
                    "vcpus": 200,
                    "ram": 512,
                    "timeout": 120
                  }
                ]
            }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    job_id = response.json()["id"]

    response = client.get(
      auth_url + "/users/get_my_permissions",
      headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    uuid = response.json()["message"]["uuid"]

    response = client.get(
      job_url + f"/{uuid}/job",
      headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    response = client.get(
      job_url + f"/job/{job_id}",
      headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    seconds = 0
    while response.json()["status"] != "completed" and seconds < 60:
      time.sleep(5)
      response = client.get(
        job_url + f"/job/{job_id}",
        headers={"Authorization": f"Bearer {token}"}
      )
      assert response.status_code == 200
      seconds += 5
    assert seconds < 60

    ## Cleanup

    # response = client.post(
    #   auth_url + "/users/delete",
    #   json={
    #     "uuid": uuid,
    #   },
    #   headers={"Authorization": f"Bearer {token}"}
    # )
    # assert response.status_code == 200







