import logging
import uuid
import time
import queue
import os
from threading import Thread

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
    def create_container(solver_list, job_id, has_dzn, pull_policy):

        pvc_name = "job-pvc"
        pvc = client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)


        #TODO: Make sure to sanitize solver name to avoid command injection?
        container_list = []
        for solver in solver_list:
          if has_dzn:
            start_command = f"minizinc -i --output-objective --output-mode dzn /mnt/{job_id}.mzn /mnt/{job_id}.dzn"
          else:
            start_command = f"minizinc -i --output-objective --output-mode dzn /mnt/{job_id}.mzn"

          container = client.V1Container(
              image=f"{solver.name}",
              name=f"solver-{solver.name.replace('/','-')}",
              image_pull_policy=pull_policy,
              volume_mounts=[client.V1VolumeMount(name="job-pvc", mount_path='/mnt')],
              command=["sh", "-c", start_command],
          )
          container_list.append(container)

          logging.info(
              f"Created container with name: {container.name}, "
              f"image: {container.image} and solver: {solver}"
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

            pod_template = client.V1PodTemplateSpec(
                spec=client.V1PodSpec(restart_policy="Never", containers=[container], volumes=[volume]),
                metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
            )
            pod_list.append(pod_template)


        return pod_list

    @staticmethod
    def create_job(pod_templates, job_id):

        job_list = []
        index = 0
        for pod in pod_templates:
            job_name = f"{pod.metadata.name}-{index}"
            metadata = client.V1ObjectMeta(name=job_name, labels={"job": job_id})

            job = client.V1Job(
                api_version="batch/v1",
                kind="Job",
                metadata=metadata,
                spec=client.V1JobSpec(backoff_limit=0, template=pod, completions=1),
            )
            job_list.append(job)
            index += 1

        return job_list

    def start_job(self, job, batch_api, _namespace, q, job_id):
      start_time = time.time()
      batch_api.create_namespaced_job(_namespace, job)
      print(f"starting thread with job: {job.metadata.name}")

      w = watch.Watch()
      for event in w.stream(func=self.core_api.list_namespaced_pod,
                                namespace=_namespace,
                                label_selector=f"job-name={job.metadata.name}",
                                timeout_seconds=20):
          if event["object"].status.phase == "Succeeded":
              pod_name = event['object'].metadata.name
              w.stop()
              end_time = time.time()
              logging.info("Started in %0.2f sec", end_time-start_time)

              result = self.core_api.read_namespaced_pod_log(name=pod_name, namespace=_namespace)
              q.put((job.metadata.name, result))
              return

          # TODO: Clean up this code:
          # event.type: ADDED, MODIFIED, DELETED
          if event["type"] == "DELETED":
              # Pod was deleted while we were waiting for it to start.
              logging.info("Deleted before it started")
              w.stop()
              return

      print("Reached here")
      q.put(None)

      return


def thread_controller(q):
  first = q.get()
  print(f"First thread was: {first}")
  # TODO: Stop other jobs
  # TODO: Update database entry for job with result and new status
  return

def execute_job(create_job_request, mzn, dzn):

    job_id = uuid.uuid4()
    pod_id = job_id

    has_dzn = dzn != None

    with open(f"/mnt/{job_id}.mzn", "a") as f:
      f.write(mzn)
    if has_dzn:
      with open(f"/mnt/{job_id}.dzn", "a") as f:
        f.write(dzn)

    # Kubernetes instance
    k8s = Kubernetes()

    _namespace = "default"
    k8s.create_namespace(_namespace)

    _pull_policy = "IfNotPresent"

    solver_containers = k8s.create_container(create_job_request.solver_list, job_id, has_dzn, _pull_policy)

    _pod_name = f"solver-instance-pod-{pod_id}"
    _pod_specs = k8s.create_pod_template(_pod_name, solver_containers)

    jobs = k8s.create_job(_pod_specs, job_id)


    batch_api = client.BatchV1Api()
    q = queue.Queue()
    controller_thread = Thread(target = thread_controller, args = (q, ))
    controller_thread.start()
    for job in jobs:
      thread = Thread(target = k8s.start_job, args = (job, batch_api, _namespace, q, job_id))
      thread.start()


if __name__ == "__main__":
  execute_job()

