function loginFunction() {
  // call the user service

  // Set the session token
  localStorage.setItem("user_token", "jwt_token")
  
  // redirect to index
  window.location.href = "index.html";
}

// Get the input field
var input = document.getElementById("inputPassword");

// Execute a function when the user presses a key on the keyboard
input.addEventListener("keypress", function(event) {
  // If the user presses the "Enter" key on the keyboard
  if (event.key === "Enter") {
    // Cancel the default action, if needed
    event.preventDefault();
    // Trigger the button element with a click
    document.getElementById("loginButton").click();
  }
}); 

// Might be redundant
function clean(){
  document.getElementById('inputPassword').value = ''
  document.getElementById('usernameInput').value = ''
}