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


