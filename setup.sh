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
  --build-arg AUTH_PRIVATE_KEY=LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JSUV2Z0lCQURBTkJna3Foa2lHOXcwQkFRRUZBQVNDQktnd2dnU2tBZ0VBQW9JQkFRQytrQmNQR0xPZzNnd2UKelNvbXREMG44Tno3M21ZdHRQdWorRnJEYTllNEhZdWhLbnpubGIvbUdrK3JLRUNRK1lva1RNZ0tub3A3dlpyYQpoUlY0bHZ5VnlRemVTYjEzRVVHODJ4c3dTa29RNDdYOWFHWmJEeG9QQUVqc1RTenNvQmNkSjJvSUdkd0hndmRiCmZzNzF6cHREWkNzYWwrczN6YklWZDdQYm0xMi9VNE56dHZOOWdWMFBrc2MxWEtaaVhRVDUxSC9nL1kvLzVqRlIKZnVpWlFqMEdxM3FOM0RxNFJHM2ExekpQUThWUFlOREIvZWEydGNLNStqcnk0eC9Fby9STTNselZscWZpUEJkNgpJa1RqQWMvTVdCcFpQT0FvSHJGckltcVNBajJlSExrcG80MGdwNzVrSjZ1dXdFck8yVDFIeTRmZndaMGphdHpBCkk5aUxZQ1NSQWdNQkFBRUNnZ0VBS1RiRXBmRXp1RkVOMGdPUllEbVBHSHBSY08vU3JZUDlBS09RRGIvZk1lVEIKOUNOYVRFUG84djB4eWRTMDBpWUdLSCtxckJGSjVpVkZ2b2tWOGJUR0FDY3hiMG9IZmg3dlZzY1VoRWNzNmFZMgpFQTVxUkx0cGFXRW9aR0wwbW1DdFh4TE5MZDlaNVE0QUxYdXBpeVFhRkdNdnAxcS85cHU0TGtoclQ4MjBZdEp2CkRBazk2dG13OVRPeFJMUGxCd21pNGNuUEh1TE5VZm4zdWkveDNGbkczbnZYYnFvOFVXalBwV0FRb3d3bnlhUzMKZTAvTWw2TGxtUnJGbDQ2S0UrTmR0QjZacU1OUDU2VWx2cU8yMFYzVGxJUjNUbDMrTjNTZ3hhZ3A3aWhrY1VyaAo4QzcwZERwQUZCSlhNQ29zS01SbkhyUTBZREtPenRURzIvMzhBM1NYT1FLQmdRRDBuZUdBNXZzdndTV29XZWVsCm9RbjRJMnhNcEFIZWpiZHhEUE1tREc4VlpNZ3Q4MERjZkJuYkR1L3hLVXlPaGRhV2dRTmtOd0pGYjFXVmFaM28KanBYYUpudVdWNjhSRGhjVGpoZmpScDRpejUwbm4raWlzc25NUjArclAxMkdiYzFXeVUwUzBFZnJJTzc1V0Zhbwo5N1lpZkFwWGNVMHNVV3ZndE9abnJxb2Yvd0tCZ1FESGJrUHlkYnRqaTlLZHY1WHFWNmQ0UnJNSGpiZmpOVy8rClhBZ09lV1hCQVBNTTFxOUErM05YVmVWNytNTWNQYW9qdG45NmRDYXlwUHFSeFhLelVmemhETEtBYlB0V0N6WmQKZVRlTFVCWkl4dnFyMzJveEpvaUNqbm5iZmhmS2U5cTQrcENOSE1kWXcvUlVoTEp6QWppWmZsczdaOHFjVytJTwpXQmZvMWNPN2J3S0JnUUN1Y0RRU1p5VXpIY3FMN21qNXZRaE44bnpWZnBOeXNKN2pPSGZnWnplRUN4V1Jad21XCjhjekNZVG1NUVlZOWtJWEJXQWtpR3ZROHJiTmJWRER1V1ZmVmRHSG5pV25uZ0tQR0p5c3p3UFVlSCsyVEJ6NnYKWDAzMnBkZlRaK0Y2N3F4aXVqU0RPUkpBUTRFSFFRNnplY3BoZHhFczREaEhaVnpIcGxrMEVPTnk0d0tCZ0RaNgpzY2NYVUZSMlN0ZmJFV29OL2VyR2JYdS94QjhtWnV5MldXRVMyckFwd1R1ZG5neURaRlBVWERkTWtvZ3hkRHdEClM3bTQ1eVZnR2k4ZUlDSktZR2xlSFprbHJGY3FBdlR2K3pOc2NsbjVPVnNnVWhNUk1yTnZsbXhXZXN0T29FWnQKOUhVSUNwRCtIczNEM2plNndKbDF3aGh0VnhUMXFNQkFZbSt4amFHekFvR0JBT2VBMmJSYjQrTGN3NzRhQitzdgpNbzQrWkNkMmVGM3d2dDNnSGFjcGp1UnJ6MDFwQlphTjNFVThMZmJRRWQ1M0NJN2gxOThMaHdRVmRYclJKaHVICnZtdGhYRHpLY0g4NjZndm9ZMncya2k3djJLWkJwejJER1FNMHlnZksrY2dtNURPcU1ZRzhYbHVNai9TcmtBZngKanhQYllHY0RDQVdOMHBLc0lQSUgyb2h4Ci0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS0K
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
