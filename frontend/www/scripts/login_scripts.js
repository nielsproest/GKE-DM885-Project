
const authUrl = "http://127.0.0.4:5000"

function loginFunction() {

  const usernameField = document.querySelector('input[type="text"]');
  const pwField = document.querySelector('input[type="password"]');

  // call the user service
  if (authUrl != null) {
    fetch(authUrl + "/users/login" , {
      method: 'POST',
      body: '{"username":"' + usernameField.value + '", "password":"' + pwField.value + '"}',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*',
        'Content-Type': 'application/json',
        'accept': 'application/json'
      }
    })
      .then((response) => response.json())
      .then((result) => {

        // Put JWT in session
        localStorage.setItem("user_token", result.token)

        window.location.href = "index.html";
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }
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