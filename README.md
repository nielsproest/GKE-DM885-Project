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

You will likely need to enable more APIs on the google cloud project.

