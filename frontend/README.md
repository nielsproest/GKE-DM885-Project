## Running the frontend

# run in docker image

1. Run the following cmd to get the image to your docker:
	```
	docker build -t frontend_webserver .
	```

2. Check that you have the image using:
	```
	docker image ls
	```

3. Run the image with an nginx server and expose it on port 3000 using:
	```
	docker run  -p 3000:80 --rm frontend_webserver
	```

4. Check the project on url: localhost:3000

# run locally


1. Install serve using npm:
	```
	npm install serve
	```

2. Run serve from the www folder:
 	```
	serve
	```

3. Check the project on url: localhost:3000