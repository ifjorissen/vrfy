import os
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from course import models
from util import tango
from vrfy.settings import MEDIA_ROOT

@receiver(pre_delete, sender=models.GraderLib)
def my_handler(sender, **kwargs):
  gl = kwargs.get("instance")
  os.remove(MEDIA_ROOT + gl.lib_upload.name)#removes if from problem_assets
  name = gl.lib_upload.name.split("/")[-1]
  #remove all of the instances of it in tango
  for ps in models.ProblemSet.objects.all():
    for problem in ps.problems.all():
      tango.delete(problem, ps, name)
