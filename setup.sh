#!/bin/bash
#Used to easily test the entire project on your repository
set -e

#NOTICE: CHANGE THESE
export PROJECT_ID=noted-flash-366811
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
sed "s/POSTGRES_USER[^\"]*/POSTGRES_USER=${AUTH_DB_USER}/" auth_service/.env | tee auth_service/.env
sed "s/POSTGRES_PASSWORD[^\"]*/POSTGRES_PASSWORD=${AUTH_DB_PASS}/" auth_service/.env | tee auth_service/.env
sed "s/DEFAULT_ADMIN_USERNAME[^\"]*/DEFAULT_ADMIN_USERNAME=${AUTH_ADMIN_USER}/" auth_service/.env | tee auth_service/.env
sed "s/DEFAULT_ADMIN_PASSWORD[^\"]*/DEFAULT_ADMIN_PASSWORD=${AUTH_ADMIN_PASS}/" auth_service/.env | tee auth_service/.env

echo 
echo Please run:
echo
echo To use with Ubuntu
echo Install gcloud: https://cloud.google.com/sdk/docs/install#linux
echo Run these commands:
echo gcloud auth login
echo gcloud auth application-default login
echo gcloud components update
echo 
echo Install kubectl v1.23, dont install a newer version
echo sudo snap install kubectl --channel=1.23/stable --classic
echo https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
echo 
echo Install docker
echo WARNING: Terraform may fail in svc-account.tf, you may need to change workload_identity_pool_id to something else
echo Please follow these steps and press enter \(or ignore them if you\'ve done this before\)
read varname
gcloud config set project ${PROJECT_ID}
gcloud services enable compute.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable container.googleapis.com


echo "Terraform apply"
cd terraform
printf "project_id = \"${PROJECT_ID}\"\nregion = \"${GAR_LOCATION}\"\n" > terraform.tfvars
terraform init --upgrade
terraform apply
cd ..

gcloud auth configure-docker
echo 
echo Please run:
echo
echo gcloud components install gke-gcloud-auth-plugin
echo Please follow these steps and press enter
read varname
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
