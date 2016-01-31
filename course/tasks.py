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
from django.utils.dateparse import parse_datetime

import time
import datetime
import json

#IFJ 1.20.16: TO DO: set up celery task queues

@shared_task(bind=True, max_retries=5)
def send_file_to_tango(self, ps_id, p_id, reedie_id, localfile, file_data):
  '''
  given the pk for a :model:`course.StudentProblemSolution`, figure out if it needs to get sent to tango
  '''
  #try to get the problem, the reedie, and the problem set
  reedie = Reedie.objects.get(pk=reedie_id)
  ps = ProblemSet.objects.get(pk=ps_id, pub_date__lte=timezone.now(), cs_section__in=reedie.enrolled.all())
  problem = Problem.objects.get(pk=p_id)
  r = tango.upload(problem, ps, localfile, file_data)
  if r.status_code is not 200:
    message="Failed to upload file"
    self.retry(message=message, countdown=1)
  return r

@shared_task(bind=True, max_retries=5)
def submit_job_to_tango(self, results, spsol_id, prob_result_id, files, jobName, timeout):
  student_psol = StudentProblemSolution.objects.get(pk=spsol_id)
  ps = student_psol.student_problem_set.problem_set
  problem = student_psol.problem
  tango_callback_url = "http://localhost:8000/notifyURL/student-solution{}/problem-result{}/".format(spsol_id, prob_result_id)
  r = tango.addJob(
                problem,
                ps,
                files,
                jobName,
                jobName,
                timeout=timeout,
                callback_url=tango_callback_url)
  if r.status_code is not 200:
    message = "Failed to submit job"
    self.retry(message=message, countdown=1)
  else:
    response = r.json()
    job_id = response["jobId"]
  return job_id

@shared_task(ignore_result=True) 
def get_response(job_id, prob_result_id):
  prob_result = ProblemResult.objects.get(pk=prob_result_id)
  student_psol = StudentProblemSolution.objects.get(pk=prob_result.sp_sol.id)
  student_psol.job_id = job_id
  prob_result.job_id = job_id
  student_psol.save()
  prob_result.save()

@shared_task(ignore_result=True)
def save_autograde_results(spsol_id, prob_result_id, tango_result):
  #try to find the solution and the result we made
  #if not, return the hw 
  prob_result = ProblemResult.objects.get(pk=prob_result_id)
  solution = StudentProblemSolution.objects.get(pk=spsol_id)

  lines = tango_result.splitlines()
  job_id = lines[0].split(":")[4]
  jobID = prob_result.job_id
  status = lines[4]
  tango_time = lines[0].split("[")[1].split("]")[0]
  tango_time = time.strftime(
      "%Y-%m-%d %H:%M:%S",
      time.strptime(
          tango_time,
          '%a %b %d %H:%M:%S %Y'))
  tango_time = parse_datetime(tango_time)
  tango_time = timezone.make_aware(
      tango_time, timezone=timezone.UTC())
  if "Autodriver: Job exited with status 0" in status:
      #process normally
    try: 
      #the output from the session is in the last line
      log_data = lines[-1]
      json_log = json.loads(log_data)
      score = json_log["score_sum"]
      prob_result.max_score = json_log["max_score"]
    except (ValueError, IndexError, TypeError):
      score = 0
      json_log = {'score_sum': '0', 'external_log': ["We weren't able to parse the output from the autograder. Please let your professor know."]}

  #case where timeout reached but the job wasn't "killed"
  #(really only seems to happen when we encounter an infinite loop with a print statement)
  elif "Autodriver: Job exited with status 2" in status:
    #in this case there won't be any json output
    #update the result
    score = 0
    prob_result.json_log = {'score_sum': '0', 'external_log': [
      "We had some trouble autograding your solution. This kind of error usually occurs when there are too many print statements. Please check your code."]}

  #case where the job times out
  elif "Autodriver: Job timed out after " in status:
    timeout = status.split(" ")[-2]
    #update the result
    score = 0
    json_log = {'score_sum': '0', 'external_log': [
      "Hmmm. It looks like your program timed out after " + timeout + " seconds."]}

  else:
    #we have no idea what happened
    score = 0
    json_log = {'score_sum': '0', 'external_log': ["We weren't able to parse the output from the autograder. Please let your professor know."]}

  if prob_result.timestamp is None:
    prob_result.timestamp = tango_time

  prob_result.score = score
  prob_result.json_log = json_log
  prob_result.raw_output = tango_result
  prob_result.save()

  return
