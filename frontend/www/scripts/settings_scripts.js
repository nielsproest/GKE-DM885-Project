const solverUrl = "http://127.0.0.1:8000"

function loadChecker(){
  // Can the user be here? (is admin)

  // Load admin details
  loadSolvers()
}

function loadSolvers(){

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

function makeUserAdmin() {

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


function uploadNewSolver() {

  solverName = document.getElementById("solver_id_input").value;
  newsolverUrl = document.getElementById("solver_url_input").value;  

  if(solverUrl != null){
    fetch(solverUrl + "/solver/" + solverName + "/" + newsolverUrl, {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*'
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
    fetch(solverUrl + "/solver/{id}?solverId=" + solverId, {
      method: 'DELETE',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*'
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

function logout(){
          // Delete session token

          // Back to login 
          window.location.href = "login.html";
}