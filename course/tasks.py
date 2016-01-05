#tasks
# submit solution
# reassess solution
# should both be async. main difference is that reassess takes a higher priority

from __future__ import absolute_import

# from vrfy.celery import app
# from vrfy.celery import shared_task
from celery import shared_task

# @app.task
@shared_task
def test(param):
    return 'The test task executed with argument "%s" ' % param


@shared_task
def create_spsol(ps_id, problem_id):
    '''
    given a problem id and a problem set id , return the appropriate student solution and problem set objects
    '''
    pass

@shared_task
def send_spsol_tango(spsol):
  '''
  given an student problem solution, figure out if it needs to get sent to tango
  '''
  pass