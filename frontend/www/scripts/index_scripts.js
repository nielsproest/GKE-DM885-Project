
document.getElementById("bodyIdIndex").onload = function() {onLoad()};

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

// urls for services
//const jobUrl = "http://127.0.0.1:8000" // Not finished
const jobUrl = null
const solverUrl = "http://127.0.0.1:8000"

function onLoad(){
    // Is user logged in?
    if (localStorage.getItem("user_token") === null) {
      window.location.href = "login.html";
    } 

    // Find the available solvers and available models and load the check buttons for the available solvers
    getAvailableSolvers()
    getAvailableModels()

    // Activate the settings button (if admin user)
    isUserAdmin()

    // Calls DB that holds solutions
    getSolvedSolutions()
}

function uploadModel(){
    // Calls job service and uploads a model for solving along with wanted solvers
}

function deleteSolution(){
    // Calls DB(?) to remove a certain solution
    
}

function getAvailableSolvers(){
    // Get the list of solvers the user has available

    if(solverUrl != null){
      fetch(solverUrl + "/solver", {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Access-Control-Allow-Origin':'*'
        }
      })
        .then((response) => response.json())
        .then((result) => {

          solverList = document.getElementById("solverSelectWrapper")
          solverList.innerHTML = "";
          let solverParser = new DOMParser();
          
          result.forEach(solver => {
            let solverToAppend = solverParser.parseFromString('<input type="checkbox" class="btn-check" id="btn-check-' + solver.name + '" checked autocomplete="on"><label class="btn btn-outline-primary m-1" for="btn-check-'+ solver.name +'">' + solver.name + '</label>', 'text/html')
            solverList.append(solverToAppend.childNodes[0].childNodes[1].childNodes[0])
            solverList.append(solverToAppend.childNodes[0].childNodes[1].childNodes[0])
          })
          
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    } 
}

function getAvailableModels(){
    // Get the list of models  the user has available
}

function isUserAdmin(){
    // Check token to see if user is admin
}

function getSolvedSolutions(){
    // Get solved solutions from job service 
    wrapperDiv = document.getElementById("runningSolutionsWrapper")

    if (jobUrl != null) {
      fetch(jobUrl + "/job", {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Access-Control-Allow-Origin':'*'
        }
      })
        .then((response) => response.json())
        .then((result) => {

          let jobParser = new DOMParser();
          
          result.forEach(element => {

            if(element.status == "running"){
              //Build a solver html div
              runningSolutionDiv = document.createElement("div");
              runningSolutionDiv.id = "runningSolution-" + element.id
              runningSolutionDiv.classList.add("runningSolution")
              runningSolutionDiv.classList.add("m-3")

              runningSolutionP = document.createElement("p");
              runningSolutionP.id = "running_solver_instance_header" + element.id
              runningSolutionP.classList.add("mt-1")
              runningSolutionP.classList.add("d-flex")
              runningSolutionP.classList.add("w-100")
              runningSolutionP.classList.add("justify-content-between")


              runningSolutionSpan = document.createElement("span");
              runningSolutionSpan.textContent = "Name: missing, Started: " + element.time_created
              
              runningSolutionP.appendChild(runningSolutionSpan)

              let runningJob = jobParser.parseFromString('<button id="' + element.id + '" class="btn btn-outline-danger btn-sm" onclick="stopRunningJob(this.id)" type="button">Delete job</button>', 'text/html')
              runningSolutionP.append(runningJob.documentElement)

              runningSolutionUL = document.createElement("ul");
              runningSolutionUL.id = "running_instance_solver_list" + element.id
              runningSolutionUL.classList.add("list-group")
              
              getRunningSolvers(element.id, runningSolutionUL);
              
              runningSolutionDiv.appendChild(runningSolutionP)
              runningSolutionDiv.appendChild(runningSolutionUL)
              wrapperDiv.appendChild(runningSolutionDiv);

            } else {
              
              getStoppedSolvers();

            }
          });
  
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    }

    // Is the running justs empty?
    let wrapperRunningJobs = document.getElementById("runningSolutionsWrapper");
    let runningChildCount = wrapperRunningJobs.childElementCount;
    if(runningChildCount == 0){
      wrapperRunningJobs.innerHTML = "<h4 class='m-3'>You have no running jobs</h4>"
    }

    let wrapperFinishedJobs = document.getElementById("accordionWrapper");
    let finishedChildCount = wrapperFinishedJobs.childElementCount;
    if(finishedChildCount == 0){
      wrapperFinishedJobs.innerHTML = "<h4 class='m-3'>You have no finished jobs</h4>"
    }
}

function getRunningSolvers(solutionInstanceId, runningSolutionUL){

  console.log(solutionInstanceId)

  fetch(jobUrl + "/job/" + solutionInstanceId + "/solvers", {
    method: 'GET',
    mode: 'cors',
    headers: {
      'Access-Control-Allow-Origin':'*'
    }
  })
    .then((response) => response.json())
    .then((result) => {

      let instanceParser = new DOMParser();
      
      result.forEach(instance => {

        let listItem = instanceParser.parseFromString('<li class="list-group-item">Solver: ' + instance.name + '<button id="' + instance.id + '" class="btn btn-outline-danger btn-sm position-absolute top-50 end-0 translate-middle-y" onClick="stopInstance(this.id)" type="button">Remove running solver</button></li>', 'text/html')
        runningSolutionUL.append(listItem.documentElement)

      });


    })
    .catch((error) => {
      console.error('Error:', error);
    });

}

function getStoppedSolvers(){

}

function stopRunningJob(jobId){
  console.log("Stopped job: " + jobId)

  jobToDelete = document.getElementById("runningSolution-" + jobId);
  jobToDelete.remove();

  // fetch(jobUrl + "/job/" + jobId, {
  //   method: 'DELETE',
  //   mode: 'cors',
  //   headers: {
  //     'Access-Control-Allow-Origin':'*'
  //   }
  // })
  //   .then((response) => response.json())
  //   .then((result) => {

      

  //   })
  //   .catch((error) => {
  //     console.error('Error:', error);
  //   });

  let wrapper = document.getElementById("runningSolutionsWrapper");
  let childCount = wrapper.childElementCount;
  if (childCount == 0){
    wrapper.innerHTML = "<h4 class='m-3'>You have no running jobs</h4>"
  }

}

function stopInstance(instanceId){
  console.log("Stopped instance: " + instanceId)
}


function logout(){
    // Delete session token
    localStorage.removeItem("user_token");

    // Back to login 
    window.location.href = "login.html";
}