#tasks
# submit solution
# reassess solution
# should both be async. main difference is that reassess takes a higher priority

from __future__ import absolute_import

# from vrfy.celery import app
# from vrfy.celery import shared_task
from celery import shared_task

#TO DO: set up celery task queues

# @app.task
@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param


@shared_task
def send_spsol_tango(spsol_id):
  '''
  given the pk for a :model:`course.StudentProblemSolution`, figure out if it needs to get sent to tango
  '''
  #get the solution
  #get the files
  #send the job to tango
  pass

@shared_task
def get_spsol_result_tango(spsol_id):
  '''
  given a celery task id(?) get the solution from tango and save it in a problem result
  '''
  pass

