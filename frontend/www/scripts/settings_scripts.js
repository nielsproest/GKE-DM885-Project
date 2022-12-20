const solverUrl = "/api/solver/"
const authUrl = "/api/auth/"
const jobUrl = "/api/jobs/"
const fileUrl = "/api/fs/"

function loadChecker(){

  if (localStorage.getItem("token") === null || localStorage.getItem("token") === "defined" || parseJwt(localStorage.getItem("token")).expiration > Date.now()) {
    localStorage.removeItem("token");
    window.location.href = "login.html";
  }

  // Can the user be here? (is admin)
  isUserAdmin()

  // Load admin details
  loadSolvers()
  getAllUsers()
}

function loadSolvers(){

  if(solverUrl != null){
    fetch(solverUrl + "solver", {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        solverList = document.getElementById("solverList")
        solverList.innerHTML = "";
        let solverParser = new DOMParser();

        result.forEach(solver => {
          let solverToAppend = solverParser.parseFromString('<li class="list-group-item d-flex w-100 justify-content-between">' + solver.name + '<button id="' + solver.id + '" type="button" class="btn btn-outline-danger btn-sm" onclick="deleteSolver(this.id)">Delete solver</button></li>', 'text/html')
          solverList.append(solverToAppend.documentElement)
        })

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function getAllUsers(){

  userWrapper = document.getElementById("userWrapper")

  if(authUrl != null){
    fetch(authUrl + "users/list_users", {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        userWrapper.innerHTML = "";
        let userParser = new DOMParser();

        result.message.forEach(user => {

          accordionWrapperId = "accordionWrapper" + user.uuid

          // <small>Created: ` + user.created + `</small> In case users gets created time :)

          let userAppend = userParser.parseFromString(`
          <div id="user-object-` + user.uuid + `" class="user_object border rounded-2 m-1">
                <div class="list-group mb-3">
                  <div class="list-group-item list-group-item-action" aria-current="true">
                    <div class="d-flex w-100 justify-content-between">
                      <h5 class="mb-1">` + user.username + `</h5>

                    </div>
                    <button type="button" class="btn btn-outline-success btn-sm" data-bs-toggle="modal" data-bs-target="#setPermissionsModal" data-bs-userId="` + user.uuid + `">Set permissions</button>
                    <button id="`+ user.uuid +`" type="button" class="btn btn-outline-danger btn-sm" onclick="deleteUser(this.id)">Delete user</button>
                  </div>
                </div>

                <p class="text-start lh-1 m-3" style="color:lightskyblue;">Stopped and running solutions:</p>
                <div class="accordion" id="running-` + accordionWrapperId + `">

                </div>

                <div class="accordion" id="stopped-` + accordionWrapperId + `">

                </div>

            </div>
          `, 'text/html')

          userWrapper.append(userAppend.childNodes[0].childNodes[1].childNodes[0]);

          getSolvers("running-" + accordionWrapperId,"stopped-" + accordionWrapperId, user.uuid)
        })



      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

  if(userWrapper.childElementCount == 0){
    let userParser = new DOMParser();

    let userAppend = userParser.parseFromString(`
    <div id="user-object-GUIDFORJOHN" class="user_object border rounded-2 m-1">
          <div class="list-group mb-3">
            <div class="list-group-item list-group-item-action" aria-current="true">
              <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">John Neutralesen</h5>
                <small>Created: Fri Nov 18 10:15</small>
              </div>
              <button type="button" class="btn btn-outline-success btn-sm" data-bs-toggle="modal" data-bs-target="#setPermissionsModal" data-bs-userId="GUIDFORJOHN">Set permissions</button>
              <button id="GUIDFORJOHN" type="button" class="btn btn-outline-danger btn-sm" onclick="deleteUser(this.id)">Delete user</button>
            </div>
          </div>

          <p class="text-start lh-1 m-3" style="color:lightskyblue;">Johns running solvers:</p>

          <div class="accordion" id="accordionWrapper">
            <div class="accordion-item">
              <h2 class="accordion-header" id="headingOne">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                  Running job: BIBD2.mzn. Started: 9:49
                </button>
              </h2>
              <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                <div class="accordion-body">
                  <div id="runningSolutionsWrapper">
                    <div class="runningSolution m-3 border rounded-2">
                      <p class="text-start lh-1 m-2" style="color:lightskyblue;">Running job: BIBD2.mzn. Started: 9:49 <button class="btn btn-outline-danger btn-sm" type="button">Delete job</button></p>
                      <ul class="list-group">
                        <li class="list-group-item">Solver: gecode <button class="btn btn-outline-danger btn-sm position-absolute top-50 end-0 translate-middle-y" type="button">Remove running solver</button></li>
                        <li class="list-group-item">Solver: chuffed <button class="btn btn-outline-danger btn-sm position-absolute top-50 end-0 translate-middle-y" type="button">Remove running solver</button></li>
                        <li class="list-group-item">Solver: OR-Tools <button class="btn btn-outline-danger btn-sm position-absolute top-50 end-0 translate-middle-y" type="button">Remove running solver</button></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
        </div>
      </div>
    `, 'text/html')

    userWrapper.append(userAppend.childNodes[0].childNodes[1].childNodes[0]);

  }

}

function getSolvers(runningwrapperId, stoppedwrapperId, userId){

  if (jobUrl != null) {
    fetch(jobUrl + userId + "/job", {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        runningSolversElement = document.getElementById(runningwrapperId)
        runningSolversElement = document.getElementById(stoppedwrapperId)
        let solverParser = new DOMParser();

        result.forEach(job => {

          var counter = 0;

          if(job.status == "running"){

            runningSolvers = solverParser.parseFromString(`
              <div class="accordion-item">
                <h2 class="accordion-header" id="heading-`+ userId +`">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#running-collapse-`+userId + counter + `" aria-expanded="true" aria-controls="collapseOne">
                    Running job: ` + job.solver + `. Started: ` + job.time_created + `
                  </button>
                </h2>
                <div id="running-collapse-`+ userId + counter + `" class="accordion-collapse collapse" aria-labelledby="heading-`+ userId +`" data-bs-parent="#accordionExample">
                  <div class="accordion-body">
                    <div id="runningSolutionsWrapper-`+ userId + counter + `">
                      <div id="runningSolution-` + job.id + `" class="runningSolution m-3 border rounded-2">
                        <p class="text-start lh-1 m-2" style="color:lightskyblue;"> Running job: ` + job.name + `. Started: ` + job.time_created + ` <button id="` + job.id + `" class="btn btn-outline-danger btn-sm m-3" type="button" onclick="deleteRunningJob(this.id)">Delete job</button></p>
                        <ul id="running-instance-list-` + job.id + `" class="list-group">
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            `, 'text/html');

            runningSolversElement.append(runningSolvers.childNodes[0].childNodes[1].childNodes[0]);
            getRunningInstances("running-instance-list-" + job.id, job.id);

          } else {

            stoppedSolvers = solverParser.parseFromString(`
            <div class="accordion-item">
              <h2 class="accordion-header" id="headingstopped-`+ userId + counter +`">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#stopped-collapse-`+ userId + counter + `" aria-expanded="true" aria-controls="collapseOne">
                  Solution: ` + job.winning_solver + `. Started: ` + job.time_created + `
                </button>
              </h2>
              <div id="stopped-collapse-`+ userId + counter + `" class="accordion-collapse collapse" aria-labelledby="headingstopped-`+ userId + counter +`" data-bs-parent="#accordionExample">
                <div class="accordion-body">
                  <div id="stoppedSolutionsWrapper-`+ userId + counter + `">
                    <p class="text-start lh-1 m-2" style="color:lightskyblue;"> Job: ` + job.name + `. Started: ` + job.time_created + `</p>
                    <div id="runningSolution-` + job.id + `" class="runningSolution m-3 border rounded-2">

                      <div><span class="badge badge-primary m-1">Results:</span> ` + job.result.replace(/\n/g, '<br>') + `</div>
                      <button id="` + job.id + `" class="btn btn-outline-danger btn-sm m-3" type="button" onclick="deleteRunningJob(this.id)">Delete job</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          `, 'text/html');

          runningSolversElement.append(stoppedSolvers.childNodes[0].childNodes[1].childNodes[0]);

          }

          counter = counter + 1;
        })

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function getRunningInstances(instanceWrapper, jobId){

  fetch(jobUrl + "job/" + jobId + "/solvers", {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        runningInstanceElement = document.getElementById(instanceWrapper)
        let instanceParser = new DOMParser();

        runningInstanceElement.innerHTML = "";

        result.forEach(instance => {

          let listItem = instanceParser.parseFromString('<li id="runningSolverId-' + instance.id + '" class="list-group-item">Solver: ' + instance.name + '<button id="' + instance.id + '" class="btn btn-outline-danger btn-sm position-absolute top-50 end-0 translate-middle-y" onClick="deleteRunningSolver(this.id, ' + jobId + ')" type="button">Remove running solver</button></li>', 'text/html')
          runningInstanceElement.append(listItem.childNodes[0].childNodes[1].childNodes[0])

        });


      })
      .catch((error) => {
        console.error('Error:', error);
      });
}

const exampleModal = document.getElementById('setPermissionsModal')
exampleModal.addEventListener('show.bs.modal', event => {
  // Button that triggered the modal
  const button = event.relatedTarget
  // Extract info from data-bs-* attributes
  const recipient = button.getAttribute('data-bs-userId')
  // If necessary, you could initiate an AJAX request here
  // and then do the updating in a callback.

  // Update the modal's content.
  const modalTitle = exampleModal.querySelector('.modal-title')
  modalTitle.innerHTML = "User id: " + recipient
  exampleModal.querySelector('.modal-btn-class').id = recipient

  // console.log("testing", recipient)
  modalTitle.value = `Set permissions for ${recipient}`
})

function deleteRunningSolver(jobId,solverId){

  console.log("Trying to delete running solver:",jobId, solverId)

  fetch(jobUrl + "job/" + jobId + "/" + solverId, {
    method: 'DELETE',
    mode: 'cors',
    headers: {
      'Access-Control-Allow-Origin':'*',
      'Authorization':'Bearer ' + localStorage.getItem("token")
    }
  })
    .then((response) => response.json())
    .then((result) => {

      console.log("stop instance: ", result)
      jobToDelete = document.getElementById("runningSolverId-" + solverId);
      jobToDelete.remove();

      getAllUsers()

    })
    .catch((error) => {
      console.error('Error:', error);
    });

}

function deleteRunningJob(jobId){

  fetch(jobUrl + "job/" + jobId, {
    method: 'DELETE',
    mode: 'cors',
    headers: {
      'Access-Control-Allow-Origin':'*',
      'Authorization':'Bearer ' + localStorage.getItem("token")
    }
  })
    .then((response) => response.json())
    .then((result) => {

      console.log("stop job: ", result)
      jobToDelete = document.getElementById("runningSolution-" + jobId);
      jobToDelete.remove();

      getAllUsers()

    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

function uploadNewSolver() {

  solverName = document.getElementById("solver_id_input").value;
  newsolverUrl = document.getElementById("solver_url_input").value;

  if(solverUrl != null){
    fetch(solverUrl + "solver/" + solverName, {
      method: 'POST',
      mode: 'cors',
      body: JSON.stringify({
        "image": newsolverUrl
      }),
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Content-Type': 'application/json',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {
        console.log("Upload solver: ", result)

        if(result == "success"){
          loadSolvers()
          document.getElementById("solverWarningDiv").modal('hide')
        } else {
          warningDiv = document.getElementById("solverWarningDiv");
          let warningString = '<div class="alert alert-warning alert-dismissible fade show" role="alert">'+ result.detail +'<button type="button" class="btn-close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>'

          warningDiv.innerHTML = warningString;
        }

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

}

function deleteSolver(solverId) {

  if(solverUrl != null){
    fetch(solverUrl + "solver/" + solverId, {
      method: 'DELETE',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        console.log(result)
        loadSolvers()

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

}

function isUserAdmin(){
  // Check token to see if user is admin

  if (authUrl != null) {
    fetch(authUrl + "users/get_my_permissions" , {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        console.log("permissions results:", result)

        if(result.message.is_admin != true){
          localStorage.removeItem("token");
          window.location.href = "login.html";
        }

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function setPermissions(userId){
  // Set permissions

  var data = new FormData()
  cpu = document.getElementById("user_cpu_input").value;
  ram = document.getElementById("user_ram_input").value;
  admin = document.querySelector('#admin_checkbox').checked;

  data.append("vcpu", cpu)
  data.append("ram", ram)
  data.append("is_admin", admin)

  if(authUrl != null){
    fetch(authUrl + "users/modify" , {
      method: 'POST',
      mode: 'cors',
      body: JSON.stringify({
        "uuid": userId,
        "data": {
            "vcpu": cpu,
            "ram": ram,
            "is_admin": admin
        }
      }),
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Content-Type': 'application/json',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        console.log("permissions results:", result)

        if("token" in result){
          localStorage.setItem("token", result.token)
          document.getElementById("solverWarningDiv").modal('hide')
        }

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function deleteUser(userId){

  if(authUrl != null){
    fetch(authUrl + "users/delete" , {
      method: 'POST',
      mode: 'cors',
      body: '{"uuid":"'+ userId +'"}',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token"),
        'Content-Type': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((result) => {

        console.log("permissions results:", result)
        // Remove div
        userToDelete = document.getElementById("user-object-" + userId);
        userToDelete.remove();

        deleteAllUsersModels(userId)
        deleteAllJobs(userId)

        getAllUsers()

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function deleteAllUsersModels(userId){

  if(fileUrl != null){
    fetch(fileUrl + userId + "2/delete", {
      method: 'DELETE',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        console.log("Deleted all user model: ", result)

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

}

function deleteAllJobs(userId){

  if(jobUrl != null){
    fetch(jobUrl + "/" + userId + "/jobs", {
      method: 'DELETE',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {

        console.log("Deleted all user jobs: ", result)

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function parseJwt (token) {

  var base64Url = token.split('.')[1];

  var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');

  var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));

  return JSON.parse(jsonPayload);
}

function logout(){
  // Delete session token
  localStorage.removeItem("token")

  // Back to login
  window.location.href = "login.html";
}