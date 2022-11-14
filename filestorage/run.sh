#!/bin/sh
kubectl apply -f DB/postgres-configmap.yaml 
kubectl apply -f DB/postgres-pvc-pv.yaml 
kubectl apply -f DB/postgres-deployment.yaml 
#kubectl exec -it [pod-name] --  psql -h localhost -U admin --password -p 5432 postgresdb