from sqlalchemy.orm import Session
from sqlalchemy import delete
from dateutil import parser
import datetime
import uuid
import pytz
import executor

import models, schemas

utc=pytz.UTC

def get_job(db: Session, job_id: str, user_id: str):
    return db.query(models.Job).filter(models.Job.user_id == user_id).filter(models.Job.id == job_id).first()

def get_jobs(db: Session, user_id: str):
    return list(db.query(models.Job).filter(models.Job.user_id == user_id))

def get_solver_instances(db: Session, job_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if job:
      return list(job.solver_instances)
    else:
      return None

def get_user_from_job(db: Session, job_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if job:
      return job.user_id
    else:
      return None

def delete_job(db: Session, job_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if job:
      print("attempting to stop job")
      for solver in job.solver_instances:
        try:
          executor.stop_job(solver.id, "default")
          print(f"successfully stopped solver: {solver.id}")
        except:
          print(f"failed to stopped solver: {solver.id} (it was already stopped)")
      db.delete(job)
      db.commit()
      return job
    else:
      return None

def delete_all_jobs(db: Session, user_id: str):
    jobs = db.query(models.Job).filter(models.Job.user_id == user_id)
    if jobs:
      for job in jobs:
        db.delete(job)
      db.commit()
      return "success"
    else:
      return None

def stop_solver(db: Session, job_id: str, solver_id: str, user_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if job:
      print("attempting to stop solver")
      try:
        executor.stop_job(solver_id, "default")
        print("successfully stopped solver")
      except:
        print("failed to stopped solver (it was already stopped)")
      for solver in job.solver_instances:
        if str(solver.id) == str(solver_id):
          db.delete(solver)
          db.commit()
      return "success"
    else:
      return None

def solvers_left(db, job_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    return len(job.solver_instances)

def running_solvers_left(db, job_id: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    solver_count = 0
    for solver in job.solver_instances:
      if solver.status == "running":
        solver_count += 1
    print(f"RUNNING SOLVERS LEFT {solver_count}")
    return solver_count

def create_job(db: Session, job: schemas.CreateJob, user_id: str):
    db_job = models.Job(
      user_id=user_id,
      mzn_id=job.mzn_id,
      dzn_id=job.dzn_id,
      result="",
      winning_solver="",
      status="running")
    db.add(db_job)
    for solver in job.solver_list:
        db_solver = models.SolverInstance(
          status="running",
          name=solver.name,
          image=solver.image,
          vcpus=solver.vcpus,
          timeout=solver.timeout,
          ram=solver.ram,
          job_id=db_job.id
        )
        db_job.solver_instances.append(db_solver)

    db.commit()
    db.refresh(db_job)
    return db_job

def update_solver_instance_result(db: Session, job_id: str, solver_id: str, result: str, status: str):
    solvers = db.query(models.Job).filter(models.Job.id == job_id).first().solver_instances
    for solver in solvers:
        if str(solver.id) == str(solver_id):
          solver.result = result
          solver.status = status
          db.commit()
          return {"success"}
    return {"error"}

def found_result(db: Session, job_id: str, solver_id: str, result: str):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    job.status = "completed"
    job.result = result
    for solver in job.solver_instances:
      if str(solver.id) == str(solver_id):
        solver.status = "completed"
        job.winning_solver = solver.name
      else:
        solver.status = "stopped"

    db.commit()
    return {"success"}


def num_vcpus_in_use(db, user_id: str):
    jobs = db.query(models.Job).filter(models.Job.user_id == user_id)
    vcpu_sum = 0
    for job in jobs:
      for solver in job.solver_instances:
        if job.status == "running" and solver.time_created + datetime.timedelta(hours=1,seconds=solver.timeout) > utc.localize(datetime.datetime.now()):
          vcpu_sum += solver.vcpus
          print(vcpu_sum)
    return vcpu_sum

def ram_in_use(db, user_id: str):
    jobs = db.query(models.Job).filter(models.Job.user_id == user_id)
    ram_sum = 0
    for job in jobs:
      for solver in job.solver_instances:
        if job.status == "running" and solver.time_created + datetime.timedelta(hours=1,seconds=solver.timeout) > utc.localize(datetime.datetime.now()):
          ram_sum += solver.ram
          print(ram_sum)
    return ram_sum

def set_pod_name(db, job_id: str, solver_id: str, pod_name: str):
    solvers = db.query(models.Job).filter(models.Job.id == job_id).first().solver_instances
    for solver in solvers:
        if str(solver.id) == str(solver_id):
          solver.pod_name = pod_name
          db.commit()
          return {"success"}
    return {"error"}

def is_job_completed(db, job_id: str):
  job = db.query(models.Job).filter(models.Job.id == job_id).first()
  if job:
    return job.status == "completed"
  else:
    return True