document.getElementById("bodyIdIndex").onload = function() {onLoad()};

function onLoad(){
    // Is user logged in?
    if (localStorage.getItem("user_token") === null) {
      window.location.href = "login.html";
    } 

    // Find the available solvers and load the check buttons for the available solvers


    // Activate the settings button (if admin user)
    
    // Calls DB that holds solutions(?)
}

function uploadModel(){
    // Calls job service and uploads a model for solving along with wanted solvers
}

function deleteSolution(){
    // Calls DB(?) to remove a certain solution 
}

function logout(){
    // Delete session token
    localStorage.removeItem("user_token");

    // Back to login 
    window.location.href = "login.html";
}