To run this service, you must have a functioning postgresql service running.
I expect this to be ran in minikube, in which you can do:
	kubectl apply -f DB/postgres-configmap.yaml 
	kubectl apply -f DB/postgres-pvc-pv.yaml 
	kubectl apply -f DB/postgres-deployment.yaml 
To run a postgresql instance

To run it locally:
	cd service
	docker build -t fs_service .
	sudo mkdir /mnt/hdd
	sudo chown -R YOUR_USER:YOUR_USER /mnt/hdd
	echo Have a working postgres instance on 127.0.0.1:5432
	docker run -it --network host \
		-v /mnt/hdd:/mnt/hdd/dumbaf \
		-e POSTGRES_DB=postgres \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=postgres \
		-e _POSTGRES_HOST=127.0.0.1:5432 \
		-e _HOST=0.0.0.0:9090 \
		-e _STORAGE_DIR=/mnt/hdd/dumbaf \
		fs_service

It should now be running at 127.0.0.1:9090
To test it:
	Upload a file as user id 0:
		curl -X PUT -L -F "file=@blast2.sh" http://127.0.0.1:9090/0/
		=>
		{"message":"OK","id":0}
	List user id 0's files
		curl -X PUT -L -F "file=@blast2.sh" http://127.0.0.1:9090/0/list
		=>
		{"message":"OK","lst":[{"size":70,"id":0,"name":"blast2.sh","owner":"0"}]}
	Get user id 0's file id 0
		curl -X GET http://127.0.0.1:9090/0/0
		=>
		echo '5' > /sys/devices/platform/nct6775.656/hwmon/hwmon1/pwm4_enable
	Delete the file
		curl -X DELETE http://127.0.0.1:9090/0/0
		=>
		{"message":"OK"}