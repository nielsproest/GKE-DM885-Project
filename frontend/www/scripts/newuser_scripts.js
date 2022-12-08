  const authUrl = "http://127.0.0.4:5000"
  
  // Create user
  function createUser() {
    const usernameField = document.querySelector('input[type="text"]');
    const pwField = document.querySelector('input[type="password"]');

    // Is password identical or Is username taken?
    if (passwordDifferent() || userTaken(usernameField.value)) {
      return null;
    }

    // call the user service and create user
    if (authUrl != null) {
      fetch(authUrl + "/users/signup" , {
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

          if("details" in result){
            console.log(result)
            responsWarning(result.details)
          }else{
            // Put JWT in session
            localStorage.setItem("user_token", result.token)
    
            window.location.href = "index.html";
          }

        })
        .catch((error) => {
          console.error('Error:', error);
        });
    }
  }

  /* Is the username taken?
  * @return {Boolean}
  */
  function userTaken(username) {
    // Call to check if username is taken
    if (callToCheckUsername(username)) {
      // Show warning
      alert('Username is already taken!', 'danger');
      return true;
    }

    return false;
  }

  function responsWarning(warning){
    alert(warning, 'danger');
  }

  /* Is the 2 passwords different?
  * @return {Boolean}
  */
  function passwordDifferent () {
    // Check if passwords are different
    if (document.getElementById("inputPassword1").value != document.getElementById("inputPassword2").value) {
      // Show warning
      alert('The passwords given are not identical', 'danger');
      return true;
    }

    return false;
  }

  /* username check call
  * 
  */
 function callToCheckUsername(username){

  // Call
  fetch(authUrl + "/users/is_username_available/" + username , {
    method: 'GET',
    mode: 'cors',
    headers: {
      'Access-Control-Allow-Origin':'*'
    }
  })
    .then((response) => response.json())
    .then((result) => {
      console.log('Success:', result);
      return true
    })
    .catch((error) => {
      console.error('Error:', error);
      return false
    });
  

  //return callResult;
 }

  const alertPlaceholder = document.getElementById('alert')

  const alert = (message, type) => {
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
      `<div class="alert alert-${type} alert-dismissible" role="alert">`,
      `   <div>${message}</div>`,
      '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
      '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)
  }