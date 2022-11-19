  /* Create user
  * 
  */
  function createUser() {
    // Is password identical or Is username taken?
    if (passwordDifferent() || userTaken()) {
      return null;
    }

    // call the user service and create user

    // Verify creation

    // Wait
    
    // redirect to index
    window.location.href = "login.html";
  }

  /* Is the username taken?
  * @return {Boolean}
  */
  function userTaken() {
    // Call to check if username is taken
    if (callToCheckUsername()) {
      // Show warning
      alert('Username is already taken!', 'danger');
      return true;
    }

    return false;
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
 function callToCheckUsername(){
  // Call

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