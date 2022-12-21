# User Stories

## Regular User

A regular user wishes to solve a model.mzn that they have locally on their system and they have heard of SolveIt!.

They access the service and signup with a username (longer than 2 characters) and a password (longer than 8 characters).

Now, they login. 

Once logged in, they see a simple dashboard. It has some solvers uploaded already (sunny-cp, picat & geas).

They see the intuitive upload functionality, amazing! They upload their model.mzn and gets an instant response from the UI.

In order to solve their model, they select the solver of their dreams. Seemingly, the system chooses some default resources, so they do not choose an input. 

They start solving their model using the SolveIt! button. 

First, a running solver pops up on the left. At first, it has no input. After a few seconds, the running solver is updated with a current result.

After a few seconds more, the running solver is moved from Running solvers to completed solvers and the user can view the final result. 

Being satisfied, the user clicks the burger menu in the top right and logs out. 

## Admin

The admin has heard that a user wants  to be allowed more VCPU aswell as more RAM. Furthermore, the admin wants to add a new solver and delete an old user and all their jobs.

They go to the login page of the SolveIt! system and logs in. Once logged in, they go to the burger menu in the top right and click the settings options, which is available due to them being an admin. 

Once on the settings page, they click the "add solver" button and give it a name and a reference to the repo it is located on.

They then go through the user list and click the "delete user" button. This delete all their uploaded files and all their solutions as well as their credentials.

Finally, the admin finds the user he wants to give increased resources and clicks the "set permissions" button. In the pop up, the admin chooses the new maximum values of the user and submits them.

The admin then logs out via the burger menu.

## Silly User

A silly user stumbles across the system. 

The silly user attempt to login but is not allowed until they have signed up.

Once signed up, the silly users attempts to access the settings tab in the burger menu. They are unable to click the tab due to them not being the admin. 

The silly user then attempts to upload a .png file. Their .png does not appear since the system only allows for ".mzn" and ".dzn" files. 

The silly user finally upload a ".mzn" file and attempts to solve it with 40 vcpus. They get an error message since their user isnt allowed to use that many vcpus.

Finally, they leave their laptop for several hours. When they come back, they attempt to solve another model. Instead of it being solved, they're logged out of the system due to their token no longer being valid.
