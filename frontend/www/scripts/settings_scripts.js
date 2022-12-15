const solverUrl = "/api/solver/"
//const solverUrl = null
const authUrl = "/api/auth/"

function loadChecker(){
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
    fetch(authUrl + "list_users", {
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
        
        result.forEach(user => {

          accordionWrapperId = "accordionWrapper" + user.id 

          let userAppend = userParser.parseFromString(`
          <div class="user_object border rounded-2 m-1">
                <div class="list-group mb-3">
                  <div class="list-group-item list-group-item-action" aria-current="true">
                    <div class="d-flex w-100 justify-content-between">
                      <h5 class="mb-1">` + user.name + `</h5>
                      <small>Created: ` + user.created + `</small>
                    </div>
                    <button type="button" class="btn btn-outline-success btn-sm" data-bs-toggle="modal" data-bs-target="#setPermissionsModal" data-bs-userId="` + user.id + `">Set permissions</button>
                    <button type="button" class="btn btn-outline-danger btn-sm">Delete user</button>
                  </div>
                </div>

                <p class="text-start lh-1 m-3" style="color:lightskyblue;">` + user.name + ` running solvers:</p>

                <div class="accordion" id="` + accordionWrapperId + `">

                </div>

            </div>
          `, 'text/html')

          userWrapper.append(modelToAppend.childNodes[0].childNodes[1].childNodes[0]);

        })

        getRunningSolvers(accordionWrapperId, user.id)
        
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

  if(userWrapper.childElementCount == 0){
    let userParser = new DOMParser();

    let userAppend = userParser.parseFromString(`
    <div class="user_object border rounded-2 m-1">
          <div class="list-group mb-3">
            <div class="list-group-item list-group-item-action" aria-current="true">
              <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">John Neutralesen</h5>
                <small>Created: Fri Nov 18 10:15</small>
              </div>
              <button type="button" class="btn btn-outline-success btn-sm" data-bs-toggle="modal" data-bs-target="#setPermissionsModal" data-bs-userId="GUIDFORJOHN">Set permissions</button>
              <button type="button" class="btn btn-outline-danger btn-sm">Delete user</button>
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

function getRunningSolvers(wrapperId, userId){

  if (jobUrl != null) {
    fetch(jobUrl + "job", {
      method: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {
        
        runningSolversElement = document.getElementById(wrapperId)
        let runningSolverParser = new DOMParser();

        result.forEach(job => { 
          if(job.status == "running"){

            runningSolvers = runningSolverParser.parseFromString(`
              <div class="accordion-item">
                <h2 class="accordion-header" id="headingOne">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                    Running job: ` + job.name + `. Started: ` + job.time_created + `
                  </button>
                </h2>
                <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                  <div class="accordion-body">
                    <div id="runningSolutionsWrapper">
                      <div class="runningSolution m-3 border rounded-2">
                        <p class="text-start lh-1 m-2" style="color:lightskyblue;"> Running job: ` + job.name + `. Started: ` + job.time_created + ` <button class="btn btn-outline-danger btn-sm" type="button" onclick="deleteRunningSolver(this.id)">Delete job</button></p>
                        <ul id="running-instance-list-` + job.id + `" class="list-group">
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            `, 'text/html');

            runningSolversElement.append(runningSolvers.childNodes[0].childNodes[1].childNodes[0]);
            getRunningInstances("running-instance-list-" + job.id);

          }
        })

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function getRunningInstances(instanceWrapper){

  fetch(jobUrl + "job/" + solutionInstanceId + "/solvers", {
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
        
        result.forEach(instance => {

          let listItem = instanceParser.parseFromString('<li class="list-group-item">Solver: ' + instance.name + '<button id="' + instance.id + '" class="btn btn-outline-danger btn-sm position-absolute top-50 end-0 translate-middle-y" onClick="deleteRunningJob(this.id)" type="button">Remove running solver</button></li>', 'text/html')
          runningInstanceElement.append(listItem.documentElement)

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
  //
  // Update the modal's content.
  const modalTitle = exampleModal.querySelector('.modal-title')
  
  console.log("testing", recipient)
  modalTitle.value = `Set permissions for ${recipient}`
})

function deleteRunningSolver(){

}

function deleteRunningJob(){

}

function uploadNewSolver() {

  solverName = document.getElementById("solver_id_input").value;
  newsolverUrl = document.getElementById("solver_url_input").value;  

  if(solverUrl != null){
    fetch(solverUrl + "solver/" + solverName + "/" + newsolverUrl, {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {
        
        loadSolvers()
        
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }

}

function deleteSolver(solverId) {

  if(solverUrl != null){
    fetch(solverUrl + "solver/{id}?solverId=" + solverId, {
      method: 'DELETE',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Authorization':'Bearer ' + localStorage.getItem("token")
      }
    })
      .then((response) => response.json())
      .then((result) => {
        
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

        // Not finished
        if(result.permissions != "yay admin"){
          window.location.href = "index.html";
        }

      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
}

function logout(){
          // Delete session token

          // Back to login 
          window.location.href = "login.html";
}