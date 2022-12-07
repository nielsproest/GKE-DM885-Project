
## Testing the authentication service locally:

To run the authentication service locally, you need to have a local instance of the database running. In the `/database` folder, you can use the Dockerfile to build an image, and then run it. The database will be available on port 5432.


From here, you need to access the .env file in the root folder, and change the `DATABASE_URL` to point to your local database (the IP of the database container)


You can now build the authentication service using the Dockerfile in the root folder. This will create an image that you can run locally.

Once this is done, you can access the documentation at

`http://IP:PORT/docs`

where IP is the IP of the docker container, and PORT is the port you specified in the .env file.

## Using JWT tokens

JWT Tokens are signed using the `RS256` algorithm and the private key found at `/keys/mykey.pem`. The public key is found at `/keys/mykey.pub`. The public key is used to verify the signature of the token, and the private key is used to sign the token.

Other services can request the public key from the auth service at the endpoint
`http://IP:PORT/keys/public_key`
and use it to verify the signature of the token.

All services must implement the functions `decode_jwt` and `validate_token` found in `/internal/auth.py` as it is the responsibility of each service, to ensure that tokens are valid and not expired. Here it should be noted, that inside said file, the auth service reads the public key from a file, and not from the endpoint, which is not recommended.



The frontend would not need to handle any of this, as it would only need receive a token via.
`http://IP:PORT/users/login` or
`http://IP:PORT/users/signup`

and send it to the backend in the header of each request. If any of the requests fail, the frontend should redirect the user to the login page and request a new token. The token should be sent as a "bearer token" see: https://reqbin.com/req/adf8b77i/authorization-bearer-header

## General Usage guides

Most functionality can be seen in the documentation, but to clarify some things:

both `/users/signup` and `/users/login` are described as returning a string, it should be noted that this is the JWT token.

