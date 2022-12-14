
Install dependencies:

```
pip install -r requirements.txt
pip install "uvicorn[standard]"
```

Start db
```
(in /jobservice/db)
sudo docker build -t job_service_db ./
sudo docker run --name job_service_db -d -e POSTGRES_PASSWORD=psltest -p 5432:5432 job_service_db
```


Start web server.

```
uvicorn main:app --reload
```

Access it at localhost:8000.
The localhost:8000/docs endpoint gives a nice way to test the API.


-------------


With Minikube
```
(Remember to update .env file in /jobservice/app, with correct IP)

minikube start
eval $(minikube docker-env)
docker build -t jobservice ./job_service
docker build -t job_service_db ./job_service/db
kubectl apply -f kubernetes/jobservice.yaml

(Run 'minikube service jobservice --url' and access the resulting url)
```

To restart deployment
```
kubectl rollout restart deployment/jobservice-deployment
kubectl rollout restart deployment/postgres
kubectl rollout restart deployment/frontend-deployment
```


Reset minikube oneliner:
```
minikube delete && minikube start && eval $(minikube docker-env) && docker build -t jobservice ./job_service && docker build -t job_service_db ./job_service/db
```

Connect with gcloud
```
gcloud container clusters get-credentials solveit-369711-gke --region=europe-west4
```

http://postgres.default.svc.cluster.local:5432/
http://jobservice.default.svc.cluster.local:8080/
http://auth-service.default.svc.cluster.local:5000
http://fs-postgres.default.svc.cluster.local
