[![Build Status - GitHub](https://github.com/TroelsLind/DM885-Project/workflows/Test/badge.svg)](https://github.com/TroelsLind/DM885-Project/actions?query=workflow%3ATest)
[![Coverage Status](https://coveralls.io/repos/github/TroelsLind/DM885-Project/badge.svg?branch=main)](https://coveralls.io/github/TroelsLind/DM885-Project?branch=main)
[![CodeQL](https://github.com/TroelsLind/DM885-Project/workflows/CodeQL/badge.svg)](https://github.com/TroelsLind/DM885-Project/actions?query=workflow%3ADependency+Review)
[![Dependency Review](https://github.com/TroelsLind/DM885-Project/workflows/Dependency%20Review/badge.svg)]()

# DM885-Project
A repository for the mandatory project in DM885


# Setup guide for Google Cloud


Go to the 'terraform' directory.

Then follow this guide:
https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/google-cloud-platform-build
Though skip both the "Write configuration" and "Initialize the directory" steps (since the relevant files already exist in the 'terraform' directory).
Make sure to update the variables in 'terraform.tfvars' to point to the correct name and region.
Also make sure to install gcloud and authenticate using 'gcloud init', 'gcloud auth login' and 'gcloud auth application-default login'.

Make sure to enable the  following APIs in the project:
Google Container Registry API
Service Consumer Management API
Kubernetes Engine API

You may need to run 'terraform init -upgrade'

Make sure to install kubectl version 1.23.x (x doesn't matter, could be 1.23.14).
To authenticate, run: 'gcloud container clusters get-credentials PROJECT_NAME-gke --zone=europe-west4', (replacing PROJECT_NAME).
After that, follow this guide to get kubectl working with the cluster:
https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke

Change all instances of the project-id in the project (such as in workflows and the images in the kubernetes yaml files)

# To setup
Have a google cloud account

Create a project

Edit setup.sh with your PROJECT_ID and GAR_LOCATION

Run it and follow its instructions

Check the ip in the services section of kubernetes engine

Hopefully it works :)

(PS: You have a custom dashboard, but you can also just use google's dashboard)

# Checkout the frontend
http://35.204.80.245

# API Docs
http://35.204.80.245/api/auth/docs

http://35.204.80.245/api/fs/docs

http://35.204.80.245/api/jobs/docs

http://35.204.80.245/api/solver/docs