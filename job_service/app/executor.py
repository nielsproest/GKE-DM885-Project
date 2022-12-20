import logging
import uuid
import time
import queue
import os
from threading import Thread
import crud

from kubernetes import client
from kubernetes import config
from kubernetes import watch

logging.basicConfig(level=logging.INFO)

if os.getenv('KUBERNETES_SERVICE_HOST'):
  config.load_incluster_config()
else:
  config.load_kube_config()


class Kubernetes:
    def __init__(self):

        # Init Kubernetes
        self.core_api = client.CoreV1Api()
        self.batch_api = client.BatchV1Api()

    def create_namespace(self, namespace):

        namespaces = self.core_api.list_namespace()
        all_namespaces = []
        for ns in namespaces.items:
            all_namespaces.append(ns.metadata.name)

        if namespace in all_namespaces:
            logging.info(f"Namespace {namespace} already exists. Reusing.")
        else:
            namespace_metadata = client.V1ObjectMeta(name=namespace)
            self.core_api.create_namespace(
                client.V1Namespace(metadata=namespace_metadata)
            )
            logging.info(f"Created namespace {namespace}.")

        return namespace

    def simple_persistentvolumeclaim(self, _namespace):
        all_pvcs = self.core_api.list_persistent_volume_claim_for_all_namespaces()
        list = []
        for p in all_pvcs.items:
          list.append(p.metadata.name)
        if "job-pvc" in list:
          logging.info(f"PVC job-pvc already exists. Reusing.")
          return
        else:
          pvc = client.V1PersistentVolumeClaim(
              api_version='v1',
              kind='PersistentVolumeClaim',
              metadata=client.V1ObjectMeta(
                  name='job-pvc'
              ),
              spec=client.V1PersistentVolumeClaimSpec(
                  access_modes=[
                      'ReadWriteOnce'
                  ],
                  resources=client.V1ResourceRequirements(
                      requests={
                          'storage': '16Mi'
                      }
                  )
              )
          )

          self.core_api.create_namespaced_persistent_volume_claim(namespace=_namespace,body=pvc)
          return



    @staticmethod
    def create_container(solver_instances, job_id, has_dzn, pull_policy):

        pvc_name = "job-pvc"
        pvc = client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)


        #TODO: Make sure to sanitize solver name to avoid command injection?
        container_list = []
        for solver in solver_instances:
          if has_dzn:
            start_command = f"minizinc -i --output-objective --output-mode dzn /mnt/{job_id}.mzn /mnt/{job_id}.dzn"
          else:
            start_command = f"minizinc -i --output-objective --output-mode dzn /mnt/{job_id}.mzn"

          container = (client.V1Container(
              image=f"{solver.image}",
              name=str(solver.id),
              image_pull_policy=pull_policy,
              volume_mounts=[client.V1VolumeMount(name="job-pvc", mount_path='/mnt')],
              command=["sh", "-c", start_command],
              resources=client.V1ResourceRequirements(
                limits={"cpu": f"{solver.vcpus}m", "memory": f"{solver.ram}Mi"}),
          ), solver.timeout)
          container_list.append(container)

          logging.info(
              f"Created container with name: {container[0].name}, "
              f"image: {container[0].image} and solver: {solver}"
          )

        return container_list

    @staticmethod
    def create_pod_template(pod_name, containers):
        pod_list = []
        for container in containers:
            volume = client.V1Volume(
                name='job-pvc',
                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name="job-pvc")
            )

            pod_template = (client.V1PodTemplateSpec(
                spec=client.V1PodSpec(restart_policy="Never", containers=[container[0]], volumes=[volume]),
                metadata=client.V1ObjectMeta(name=container[0].name, labels={"pod_name": container[0].name}),
            ), container[1])
            pod_list.append(pod_template)


        return pod_list

    @staticmethod
    def create_job(pod_templates, job_id):

        job_list = []
        index = 0
        for pod in pod_templates:
            job_name = f"{pod[0].metadata.name}"
            metadata = client.V1ObjectMeta(name=job_name, labels={"job": job_id})

            job = client.V1Job(
                api_version="batch/v1",
                kind="Job",
                metadata=metadata,
                spec=client.V1JobSpec(
                  backoff_limit=0,
                  template=pod[0],
                  completions=1,
                  active_deadline_seconds=pod[1],
                  ttl_seconds_after_finished=1),
            )
            job_list.append(job)
            index += 1

        return job_list

    def start_job(self, job, batch_api, _namespace, q, job_id, timeout, db):
      batch_api.create_namespaced_job(_namespace, job)
      print(f"starting thread with job: {job.metadata.name}")
      instance_id = None

      w = watch.Watch()
      for event in w.stream(func=self.core_api.list_namespaced_pod,
                                namespace=_namespace,
                                label_selector=f"job-name={job.metadata.name}",
                                timeout_seconds=timeout):
          if event["object"].status.phase == "Running" or event["object"].status.phase == "Succeeded":
              pod_name = event['object'].metadata.name
              instance_id = pod_name.rsplit('-', 1)[0]
              w.stop()

              if crud.is_job_completed(db, job_id):
                print(f"Solver {instance_id} was pending when job was completed")
                q.put((instance_id, None))
                return

              result = ""
              log_watch = watch.Watch()
              try:
                for e in log_watch.stream(func=self.core_api.read_namespaced_pod_log, name=pod_name, namespace=_namespace):
                  print(f"[FROM LOG]: {e}")
                  result += e + "\n"
                  if e == "----------":
                    crud.update_solver_instance_result(db, job_id, instance_id, result, "running")
                  elif e == "==========":
                    crud.update_solver_instance_result(db, job_id, instance_id, result, "running")
                    q.put((instance_id, result))
                    log_watch.stop()
                    return
              except Exception as exception:
                print(exception)
                q.put((instance_id, None))
                log_watch.stop()
                return

              q.put((instance_id, None))
              return

          # TODO: Clean up this code:
          # event.type: ADDED, MODIFIED, DELETED
          if event["type"] == "DELETED" or event["type"] == "Warning" or event["object"].status.phase == "Failed":
              print(f"event['object'].status.conditions: {event['object'].status.conditions}")
              logging.info("Deleted before it started")
              w.stop()
              q.put((instance_id, None))
              return

      q.put((instance_id, None))

      return


    def thread_controller(self, q, jobs, _namespace, job_id, db):
      solver, result = q.get()
      print(f"Thread was: {solver}")
      print(f"Result was: {result}")

      if solver != None:
        if result != None:
          print(f"First solver: {solver}")
          crud.found_result(db, job_id, solver, result)
          for job in jobs:
            try:
              self.batch_api.delete_namespaced_job(name=job.metadata.name, namespace=_namespace, body = client.V1DeleteOptions(api_version='v1', kind="DeleteOptions", propagation_policy="Background") )
            except:
              print("Couldn't shut down: {solver}, since it was already shut down")
            if os.path.exists("/mnt/{job_id}.mzn"):
              os.remove("/mnt/{job_id}.mzn")
            if os.path.exists("/mnt/{job_id}.dzn"):
              os.remove("/mnt/{job_id}.dzn")
          return
        else:
          print(f"Shutting down: {solver}")
          for job in jobs:
            if str(job.metadata.name) == str(solver):
              try:
                self.batch_api.delete_namespaced_job(name=job.metadata.name, namespace=_namespace, body = client.V1DeleteOptions(api_version='v1', kind="DeleteOptions", propagation_policy="Background"))
              except:
                print("Couldn't shut down: {solver}, since it was already shut down")
          crud.update_solver_instance_result(db, job_id, solver, "[SOLVER FAILED]", "failed")
          if crud.running_solvers_left(db, job_id) > 0:
            print("Restarting thread_controller")
            self.thread_controller(q, jobs, _namespace, job_id, db)
          else:
            print("Entire Job failed")
            crud.found_result(db, job_id, None, "[JOB FAILED]")
      return

def stop_job(solver_id, _namespace):
    k8s = Kubernetes()
    batch_api = client.BatchV1Api()

    batch_api.delete_namespaced_job(name=solver_id, namespace=_namespace, body = client.V1DeleteOptions(api_version='v1', kind="DeleteOptions", propagation_policy="Background"))


def execute_job(create_job_request, mzn, dzn, db):

    job_id = str(create_job_request.id)
    pod_id = job_id
    has_dzn = dzn != None

    with open(f"/mnt/{job_id}.mzn", "w") as f:
      f.write(mzn)
    if has_dzn:
      with open(f"/mnt/{job_id}.dzn", "w") as f:
        f.write(dzn)



    # Kubernetes instance
    k8s = Kubernetes()

    _namespace = "default"
    k8s.create_namespace(_namespace)

    _pull_policy = "IfNotPresent"

    solver_containers = k8s.create_container(create_job_request.solver_instances, job_id, has_dzn, _pull_policy)

    _pod_name = f"solver-instance-pod-{pod_id}"
    _pod_specs = k8s.create_pod_template(_pod_name, solver_containers)

    jobs = k8s.create_job(_pod_specs, job_id)


    batch_api = client.BatchV1Api()
    q = queue.Queue()
    controller_thread = Thread(target = k8s.thread_controller, args = (q, jobs, _namespace, job_id, db))
    controller_thread.start()
    for job in jobs:
      thread = Thread(target = k8s.start_job, args = (job, batch_api, _namespace, q, job_id, create_job_request.timeout, db))
      thread.start()


if __name__ == "__main__":
  execute_job()










#echo "int: amount = 78; array[1..4] of int: denoms = [25, 10, 5, 1];  array[1..4] of var 0..100: counts;  constraint sum(i in 1..4) ( counts[i] * denoms[i] ) = amount;  var int: coins = sum(counts); solve minimize coins;  output [   \"coins = \", show(coins), \";\",   \"denoms = \", show(denoms), \";\",   \"counts = \", show(counts), \";\" ];" > 788698e0-4301-4c7d-b94d-85a4b3b18e56.mzn