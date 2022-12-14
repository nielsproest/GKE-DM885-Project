#!/bin/bash
#Used to easily test the entire project on your repository
set -e

#NOTICE: CHANGE THESE
export PROJECT_ID=solveit-369711
export GAR_LOCATION=europe-west4

export JOB_SERVICE_DB_IMAGE=jobservice_db
export JOB_SERVICE_IMAGE=jobservice
export FRONTEND_IMAGE=frontend
export AUTH_SERVICE_DB_IMAGE=auth_service_database
export AUTH_SERVICE_IMAGE=auth_service
export FS_SERVICE_IMAGE=fs_service


#To use with Ubuntu
#https://cloud.google.com/sdk/docs/install#linux
#gcloud auth application-default login
#sudo snap install kubectl --channel=1.23/stable --classic
#https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke


#TODO: Warnings about config, versions, etc.
#TODO: Warn about sv-account.tf, they may need to change workload_identity_pool_id

echo "Terraform apply"
cd terraform
printf "project_id = \"${PROJECT_ID}\"\nregion = \"${GAR_LOCATION}\"\n" > terraform.tfvars
terraform init --upgrade
terraform apply
cd ..

echo "Docker build"
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$AUTH_SERVICE_DB_IMAGE" \
	./auth_service/database
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$AUTH_SERVICE_IMAGE" \
	./auth_service
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$JOB_SERVICE_DB_IMAGE" \
	./job_service/db
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$JOB_SERVICE_IMAGE" \
	./job_service
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$FS_SERVICE_IMAGE" \
	./filestorage/service
#TODO: Solver service
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$FRONTEND_IMAGE" \
	./frontend

echo "Docker push"
docker push eu.gcr.io/$PROJECT_ID/$AUTH_SERVICE_DB_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$AUTH_SERVICE_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$JOB_SERVICE_DB_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$JOB_SERVICE_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$FS_SERVICE_IMAGE
#TODO: Solver service
docker push eu.gcr.io/$PROJECT_ID/$FRONTEND_IMAGE

echo "Applying kubernetes definitions"
envsubst < kubernetes/authservice.yaml | kubectl apply -f -
envsubst < kubernetes/jobservice.yaml | kubectl apply -f -
envsubst < filestorage/DB/postgres-deployment.yaml | kubectl apply -f -
envsubst < filestorage/fs-deployment.yaml | kubectl apply -f -
envsubst < kubernetes/frontend.yaml | kubectl apply -f -

echo "Done!"
