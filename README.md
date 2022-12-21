# Mandatory DM885-Project

A system allowing users to solve optimization problems using different solvers in parallel.

## Checkout the frontend

http://34.147.11.9

## API Docs

Documentation for the endpoints can be found locally in the relevant pdf files.

An interactive version of the documentation where the different endpoints can be accessed, can be found at the following addresses (make sure to get a token from the auth service, and authorize yourself with it in the GUI before you can test the other services):

http://34.147.11.9/api/auth/docs

http://34.147.11.9/api/fs/docs

http://34.147.11.9/api/jobs/docs

http://34.147.11.9/api/solver/docs

## To setup in your own Google Cloud
Create a google cloud account at: https://cloud.google.com/

Create a project.

Edit setup.sh with your PROJECT_ID (Your projects ID) and GAR_LOCATION (Your projects zone).

Run setup.sh and follow its instructions.

Check the ip in the services section of kubernetes engine after a couple of minutes.

The project should now be running in Google Cloud and be available on the ip.

A default admin user can be accessed with username: "admin" and password: "password"

Note that you have a custom dashboard, but you can also use google's dashboard if preferred.

## Setting up the pipeline with Github actions
If you want to use a pipeline (Github Actions) with the system, perform the following actions (make sure you already set up google cloud):

Create a Github Repository and push everything from the DM885-Project directory.

For every .yml file in '.github/workflows' named 'deploy-{service-name}', update the values PROJECT_ID, GKE_CLUSTER, GKE_ZONE and GAR_LOCATION to the values in the Google Cloud project for project id, cluster id and zones respectively.

For every export command in 'setup.sh', add those environment variables as Github Secrets (with the names and values given in the export commands).

Add a Github Secret 'WORKLOAD_IDENTITY_PROVIDER' and set it to the workload identity provider string, and similarly add a 'SERVICE_ACCOUNT' as a Github Secret with the value of the service_account string (these strings are printed while setup.sh is running, or they can be found in the Google Cloud Project)

Now, any pushes to the repository which changes the services will be automatically deployed.

Our project repository can be found at https://github.com/TroelsLind/DM885-Project
