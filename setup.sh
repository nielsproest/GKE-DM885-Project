#!/bin/bash
#Used to easily test the entire project on your repository
set -e

#NOTICE: CHANGE THESE
export PROJECT_ID=solveit-369711
export GAR_LOCATION=europe-west4

export JOB_SERVICE_IMAGE=jobservice
export FRONTEND_IMAGE=frontend
export AUTH_SERVICE_IMAGE=auth_service
export SOLVER_SERVICE_IMAGE=solverservice
export FS_SERVICE_IMAGE=fs_service

#Passwords
export JOB_DB_USER=postgres
export JOB_DB_PASS=psltest
export SOLVER_DB_USER=postgres
export SOLVER_DB_PASS=password
export FS_DB_USER=admin
export FS_DB_PASS=psltest

export AUTH_DB_USER=postgres
export AUTH_DB_PASS=mypassword
export AUTH_ADMIN_USER=admin
export AUTH_ADMIN_PASS=password

#Patch authservice
sed -i "s/POSTGRES_USER[^\"]*/POSTGRES_USER=${AUTH_DB_USER}/" auth_service/.env
sed -i "s/POSTGRES_PASSWORD[^\"]*/POSTGRES_PASSWORD=${AUTH_DB_PASS}/" auth_service/.env
sed -i "s/DEFAULT_ADMIN_USERNAME[^\"]*/DEFAULT_ADMIN_USERNAME=${AUTH_ADMIN_USER}/" auth_service/.env
sed -i "s/DEFAULT_ADMIN_PASSWORD[^\"]*/DEFAULT_ADMIN_PASSWORD=${AUTH_ADMIN_PASS}/" auth_service/.env

echo To use with Ubuntu
echo https://cloud.google.com/sdk/docs/install#linux
echo gcloud auth application-default login
echo gcloud components update
echo sudo snap install kubectl --channel=1.23/stable --classic
echo https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
echo Install docker

#TODO: Warnings about config, versions, etc.
#TODO: Warn about sv-account.tf, they may need to change workload_identity_pool_id

echo "Terraform apply"
cd terraform
printf "project_id = \"${PROJECT_ID}\"\nregion = \"${GAR_LOCATION}\"\n" > terraform.tfvars
terraform init --upgrade
terraform apply
cd ..

echo gcloud auth configure-docker
echo gcloud components install gke-gcloud-auth-plugin
gcloud container clusters get-credentials ${PROJECT_ID}-gke --region ${GAR_LOCATION}

echo "Docker build"
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$AUTH_SERVICE_IMAGE" \
	./auth_service
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$JOB_SERVICE_IMAGE" \
	./job_service
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$FS_SERVICE_IMAGE" \
	./filestorage/service
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$SOLVER_SERVICE_IMAGE" \
	./solver_service
docker build \
	--tag "eu.gcr.io/$PROJECT_ID/$FRONTEND_IMAGE" \
	./frontend

echo "Docker push"
docker push eu.gcr.io/$PROJECT_ID/$AUTH_SERVICE_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$JOB_SERVICE_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$FS_SERVICE_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$SOLVER_SERVICE_IMAGE
docker push eu.gcr.io/$PROJECT_ID/$FRONTEND_IMAGE

echo "Applying kubernetes definitions"
envsubst < kubernetes/authservice.yaml | kubectl apply -f -
envsubst < kubernetes/jobservice.yaml | kubectl apply -f -
envsubst < filestorage/DB/postgres-deployment.yaml | kubectl apply -f -
envsubst < filestorage/fs-deployment.yaml | kubectl apply -f -
envsubst < kubernetes/solverservice.yaml | kubectl apply -f -
envsubst < kubernetes/frontend.yaml | kubectl apply -f -

echo "Update kubernetes services"
kubectl rollout status deployment/auth-database
kubectl rollout status deployment/auth-service-deployment
kubectl rollout status deployment/postgres
kubectl rollout status deployment/jobservice-deployment
kubectl rollout status deployment/fs-postgres
kubectl rollout status deployment/fs-service
kubectl rollout status deployment/frontend-deployment
kubectl get services -o wide

#kubectl rollout restart deployment frontend-deployment

echo "Done!"
