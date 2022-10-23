# Short overview of how to get and test the computing image.

1. Run the following cmd to get the image to your docker:
	```
	docker build -t computing-node-test --build-arg modelfile=testmodel.mzn .
	```

2. Check that you have the image using:
	```
	docker image ls
	```

3. Test the image using:
	```
	docker run testing python3 modelProcess.py scripts/bibd.mzn gecode
	```

The line above should print a solution to the problem: http://pauillac.inria.fr/~contraintes/OADymPPaC/Net/tra4cp/www/Examples/Classic/BIBD/index-bibd.html as well as some statistics for the solution  
The line above can be tested with a different solver! try to change "gecode" to "chuffed"
