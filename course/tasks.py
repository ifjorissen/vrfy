from __future__ import absolute_import

#celery imports
from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from celery import group, chord, chain

#app imports
from .models import *
from catalog.models import Reedie
from util import tango
from django.utils import timezone


#IFJ 1.20.16: TO DO: set up celery task queues

# @app.task
@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param

@shared_task
def say_something(param):
    logger.info("Hello, world")
    print("howdy")
    return 'The test task executed with argument "%s" ' % param

@shared_task
def update_submission(ps_id, p_id):
    pass

@shared_task
def send_file_to_tango(ps_id, p_id, reedie_id, localfile, file_data):
  '''
  given the pk for a :model:`course.StudentProblemSolution`, figure out if it needs to get sent to tango
  '''
  print("*** SEND FILE TO TANGO ***")
  print("ps_id: {} p_id: {} reedie: {} localfile: {}".format(ps_id, p_id, reedie_id, localfile))
  print("*** SEND FILE TO TANGO END INFO ***")
  #try to get the problem 
  reedie = Reedie.objects.get(pk=reedie_id)
  ps = ProblemSet.objects.get(pk=ps_id, pub_date__lte=timezone.now(), cs_section__in=reedie.enrolled.all())
  problem = Problem.objects.get(pk=p_id)
  # logger.info("uploading file {} to tango".format(file))
  r = tango.upload(problem, ps, localfile, file_data)
  return r

@shared_task
def submit_job_to_tango(results, ps_id, p_id, reedie_id, files, jobName, timeout):
  print("*** SUBMIT JOB TO TANGO ***")
  print("ps_id: {} p_id: {} reedie: {}".format(ps_id, p_id, reedie_id))
  print("results: {} jobName: {} timeout: {}".format(results, jobName, timeout))
  print("*** SUBMIT JOB TO TANGO END INFO ***")
  reedie = Reedie.objects.get(pk=reedie_id)
  ps = ProblemSet.objects.get(pk=ps_id, pub_date__lte=timezone.now(), cs_section__in=reedie.enrolled.all())
  problem = Problem.objects.get(pk=p_id)
  r = tango.addJob(
                problem,
                ps,
                files,
                jobName,
                jobName,
                timeout=timeout)
  return r

@shared_task 
def update_results(results, student_psol_id, prob_result_id):
  prob_result = ProblemResult.objects.get(pk=prob_result_id)
  student_psol = StudentProblemSolution.objects.get(pk=student_psol_id)
  response = r.json()
  student_psol.job_id = response["jobId"]
  prob_result.job_id = response["jobId"]
  student_psol.save()
  prob_result.save()
  return r

@shared_task
def get_spsol_result_tango(spsol_id):
  '''
  given a celery task id(?) get the solution from tango and save it in a problem result
  '''
  pass

