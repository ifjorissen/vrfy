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
def submit_job_to_tango(self, results, ps_id, p_id, spsol_id, reedie_id, files, jobName, timeout):
  reedie = Reedie.objects.get(pk=reedie_id)
  ps = ProblemSet.objects.get(pk=ps_id, pub_date__lte=timezone.now(), cs_section__in=reedie.enrolled.all())
  problem = Problem.objects.get(pk=p_id)
  tango_callback_url = "http://localhost:8000/notifyURL/{}/".format(spsol_id)
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

@shared_task 
def get_response(job_id, prob_result_id):
  prob_result = ProblemResult.objects.get(pk=prob_result_id)
  student_psol = StudentProblemSolution.objects.get(pk=prob_result.sp_sol.id)
  student_psol.job_id = job_id
  prob_result.job_id = job_id
  student_psol.save()
  prob_result.save()
  return job_id

@shared_task()
def update_results(jobID, username, prob_result_id):
  print("trying to get results")
  prob_result = ProblemResult.objects.get(pk=prob_result_id)
  solution = StudentProblemSolution.objects.get(pk=prob_result.sp_sol.id)
  ps = solution.student_problem_set.problem_set
  outputFile = slugify(ps.title) + "_" + slugify(solution.problem.title) + "-" + username
  r = tango.poll(solution.problem, ps, outputFile)
  if r.status_code is 404:
    message = "job: {} not ready; 404 returned".format(jobID)
    self.retry(message=message, countdown=1)
  elif r.status_code is 200:
    raw_output = r.text
    # theres a line with an empty string after the last actual output
    # what we really want is the 4th line of the output
    try:
      line = r.text.split("\n")[-2]
      job_id = r.text.split("\n")[0].split(":")[4]
      print("job ids: {} {}".format(job_id, jobID))
      if int(job_id) == int(jobID):
        # the time is on the first line surrounded by brackets
        tango_time = r.text.split("\n")[0].split("[")[1].split("]")[0]
        tango_time = time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.strptime(
                tango_time,
                '%a %b %d %H:%M:%S %Y'))
        tango_time = parse_datetime(tango_time)
        tango_time = timezone.make_aware(
            tango_time, timezone=timezone.UTC())
        if "Autodriver: Job timed out after " in line:  # thats the text that Tango outputs when a job times out
          prob_result.score = 0
          prob_result.json_log = {'score_sum': '0', 'external_log': [
              "Program timed out after " + line.split(" ")[-2] + " seconds."]}
          prob_result.timestamp = tango_time
          prob_result.raw_output = raw_output
          prob_result.save()
        else:
          # try:
          log_data = json.loads(line)

          # create the result object
          prob_result.max_score = log_data["max_score"]
          prob_result.score = log_data["score_sum"]
          prob_result.raw_output = raw_output
          prob_result.json_log = log_data
          prob_result.timestamp = tango_time
          prob_result.save()
      else: 
        print("old results?")
        message = "job: {} not ready; 200 returned for old results {}".format(jobID, job_id)
        self.update_state(state='FAILURE')
    except IndexError:
      print("index error")
      self.update_state(state='FAILURE')
      # message = "Index error, job: {} not ready; 200 returned for old results {}".format(jobID, job_id)
      # self.retry(message=message, countdown=1, throw=False)
  else:
    print("failed")
    self.update_state(state='FAILURE')
  return r

