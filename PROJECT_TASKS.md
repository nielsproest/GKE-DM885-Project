# A list of all original tasks and their status:

## RESTful API

* create its own profile that can be access with a username and password [COMPLETED]
Visit the web interface and press signup, or use the api.
* Create, read, update and delete a .mzn instance [COMPLETED]
* Create, read, update and delete a .dzn instance [COMPLETED]
Both available in the file service
* list the name of the solvers supported  [COMPLETED]
Available in the solver service via the web interface and the api.
* trigger the execution of one or more solvers (to be executed in a concurrent way)
  giving the id of the mzn and dzn instances (only mzn if dzn is not needed),
  selecting the solvers to use and their options,
  the timeout, maximal amount of memory that can be used, number of vCPUs to use.
  When the first solver terminates finding the optimal value, all the other solver in parallel
  must be terminated [COMPLETED]
Available in the web interface and the job api.
* monitor the termination state of the solver execution returning if one of the 
  solvers have found the optimum, if a solution has been found but the solvers are
  still trying to prove the optimality (i.e., no "==========" in the solution) or
  if the solvers are running but they did not even found a solution
  (i.e., no "----------" in the solution) [COMPLETED]
Available in the web interface and the job api.
* given a computaton request, retrieve its result if terminated, what solver
  manage to solve it first and the time it took to solve it [COMPLETED]
Available in the web interface and the job api.
* cancel the execution of a computation request (terminate all the solvers 
  running for the request, delete the result otherwise) [COMPLETED]
Available in the web interface and the job api.
* stop a solver for a specific request  (e.g., if a request required to use solver
  A and B, you can stop to execute solver A letting B to continue) [COMPLETED]
Available in the web interface and the job api.
* minimal GUI support [COMPLETED]
Available in the web interface.

## The Administrator

* monitor and log the platform using a dashboard [COMPLETED]
This uses google's dashboard functionality, and is available on your own cloud.
* kill all solver executions started by a user [COMPLETED]
Available in the web interface and the job api.
* set resources quota to users (e.g., no more than 6 vCPUs in total for user X) [COMPLETED]
Available in the web interface and the auth api (as admin).
* delete a user and all his/her data [COMPLETED]
Available in the web interface and in all the apis.
* deploy the system and add new computing nodes in an easy way [PARTIALLY COMPLETED]
To add new computing nodes you have to edit terraform to change the number of nodes and run terraform apply.
* add or remove a solver. It is possible to assume that the solver to add
  satisfy the submission rules of the MiniZinc challenge (note also that you have to handle
  the case when a users asks to use a removed solver) [COMPLETED]
Available in the web interface and in the solver api.

## The User 

A user should have a maximal predefined amount of computational resources that
he or she can use (e.g., 6 vCPUs). When this threashold is passed, requests
should be serialized instead of all running in parallel. If the maximal amount
of computational resources will not allow to execute a request (e.g., asking to
solve a problem with 7 different solvers in prallel when he or she can use only
6 vCPUs) then the request should not be accepted. [NOT COMPLETED]
This would require some changes to the job service, by having a queue run job.execute instead of running it directly, this isn't currently implemented.

## The Developer

* Use continuous integration and deployment [PARTIALLY COMPLETED]
When a commit to a specific service is made, the service is automatically rebuilt and pushed to the cloud, this is partly CI/CD.
What's missing is automatic testing, given that we need the services to be running for them to be tested, we should have an "integration" cloud that's monitored for if the runtime fails, and if it doesn't we should run all the pytests in tests/.
This isn't currently done.
* Infrastructure as a Code with an automatic DevOps pipeline [COMPLETED]
This is done with github actions and terraform.
* scalable, supporting multiple users exploiting if needed more resources in the
  cloud (note: vcpus allocated to a run depending on the parameter "-p") [COMPLETED]
You can do this by changing the number of nodes in terraform by editing gke.tf's node_count, be aware that this is node pr zone, usually 3, so its a multiplicative of 3.
* have tests to test the system (unit test, integration, ...) [COMPLETED]
There are tests, but they dont run automatically.
* security (proper credential management and common standard security practices
  enforced) [PARTIALLY COMPLETED]
All secrets are hidden as github secret's (so they are hidden).
The way the auth service functions, a user is given a unrevokeable key that is valid until it expires, meaning a malicious user can be malicious for whatever the expiration date is.
The file service does not validate what the contents of each file is, but it does limit how much data each user is allowed to store, the single file size is enforced by nginx, and the fileid is an increasing integer, which means that if you find an exploit to steal files, you would be able to find them easily, as opposed to using an uuid.
* provide user stories to explain how the system is intended to be use [COMPLETED]
See USER_STORIES.md
* provide minimal documentation to deploy and run the system [COMPLETED]
See README.md
* fairness: if the resources do not allow to run all the solvers at the same time
  the jobs should be delayed and executed fairly (e.g. FIFO).
  User should therefore not wait  indefinitely to run their jobs (optional). [NOT COMPLETED]
This would also be solved by the job service queue as described previously.
