import os
import shutil
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save, post_init
from course import models
from util import tango
from vrfy.settings import MEDIA_ROOT
import logging
log = logging.getLogger(__name__)

@receiver(pre_delete, sender=models.GraderLib)
def GraderLib_pre_delete(sender, **kwargs):
  """
  Deletes the grader lib file from django and
  """
  gl = kwargs.get("instance")
  try:
    os.remove(MEDIA_ROOT + gl.lib_upload.name)#removes if from problem_assets
    name = gl.lib_upload.name.split("/")[-1]
    #remove all of the instances of it in tango
    for ps in models.ProblemSet.objects.all():
      for problem in ps.problems.all():
        if problem.autograde_problem:
          tango.delete(problem, ps, name)

  except:
    log.info("DELETE: GraderLib Could not remove {!s}".format(filename))
    pass

@receiver(pre_delete, sender=models.ProblemSet)
def ProblemSet_pre_delete(sender, **kwargs):
  """
  deletes all courselabs in tango that belong to this problem set
  """
  ps = kwargs.get("instance")
  for problem in ps.problems.all():
    if problem.autograde_problem:
      try:
        tango.delete(problem, ps)
      except:
        log.info("DELETE: ProblemSet Could not remove {!s}".format(filename))
        pass

@receiver(pre_delete, sender=models.Problem)
def Problem_pre_delete(sender, **kwargs):
  """
  deletes all courselabs in tango that belong to this problem and all grading files in django
  """
  problem = kwargs.get("instance")
  shutil.rmtree(MEDIA_ROOT + problem.get_upload_folder())#delete all the problem files
  if problem.autograde_problem:
    for ps in problem.problemset_set.all():
      try:
        tango.delete(problem, ps)
      except:
        log.info("DELETE: Problem Could not remove {!s}".format(filename))
        pass


