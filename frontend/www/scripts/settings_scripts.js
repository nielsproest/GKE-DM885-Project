function loadChecker(){
  // Can the user be here? (is admin)

  // Load admin details
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

}

function logout(){
          // Delete session token

          // Back to login 
          window.location.href = "login.html";
}