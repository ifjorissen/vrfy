from django.db import models
from generic.models import CSUser
from catalog.models import Section, Course
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.files import File
from jsonfield import JSONField
import os
import os.path
import vrfy.settings
from django.utils import timezone
from util import tango

def student_file_upload_path(instance, filename):
  #filepath should be of the form: course/folio/user/problem_set/problem/filename  (maybe add attempt number)
  problem_set = instance.student_problem_solution.student_problem_set.problem_set.title
  user = instance.student_problem_solution.student_problem_set.user.username
  problem = instance.student_problem_solution.problem
  attempt = instance.attempt_num
  course = problem.cs_course.num
  return '{0}/folio/{1}/{2}/{3}_files/v{4}/{5}'.format(course, user, slugify(problem_set), slugify(problem.title), attempt, filename)

def solution_file_upload_path(instance, filename):
  #filepath should be of the form: course/solutions/problem_set/problem/filename 
  problem = instance.problem
  file_path = problem.get_upload_folder() + filename
  if os.path.isfile(vrfy.settings.MEDIA_ROOT + file_path):
    os.remove(vrfy.settings.MEDIA_ROOT + file_path)
  return file_path

def grader_lib_upload_path(instance, filename):
  file_path = 'lib/{0}'.format(filename)
  if os.path.isfile(vrfy.settings.MEDIA_ROOT + file_path):
    os.remove(vrfy.settings.MEDIA_ROOT + file_path)
  return file_path

def grade_script_upload_path(instance, filename):
  #filepath should be of the form: course/solutions/problem_set/problem/filename 
  file_path = instance.get_upload_folder() + filename
  if os.path.isfile(vrfy.settings.MEDIA_ROOT + file_path):
    os.remove(vrfy.settings.MEDIA_ROOT + file_path)
  return file_path

class Problem(models.Model):
  title = models.CharField(max_length=200)
  cs_course = models.ForeignKey('catalog.Course', null=True)
  description = models.TextField(default='') #a short tl;dr of the problem, what to read
  statement = models.TextField(default='') #markdown compatible
  many_attempts = models.BooleanField(default=True)
  autograde_problem = models.BooleanField(default=True)
  grade_script = models.FileField(upload_to=grade_script_upload_path, null=True, blank=True)
  #one_force_rename = models.BooleanField(editable=False)#used to validate that one of the inlines is being renamed
  
  def get_upload_folder(self):
    course = self.cs_course.num
    file_path = '{0}/solutions/{1}_files/'.format(slugify(course), slugify(self.title))
    return file_path
  
  def clean(self):
    if self.autograde_problem:
      if (self.grade_script == None or self.grade_script == ""):
        raise ValidationError({'grade_script': ["This field is required.",]})
    
    #self.one_force_rename = False
    """one_force_rename = False #one idea for making sure one of the student files is renamed; doesn't work
      print(RequiredProblemFilename.objects.filter(problem=self))
      for f in RequiredProblemFilename.objects.filter(problem=self):
        print(f.force_rename)
        if f.force_rename:
          one_force_rename = True
      if not one_force_rename:
        raise ValidationError('At least one of the student files needs to be renamed. Check what student files your grading script imports.')
    """

  def __str__(self): 
    return self.title
  """
  #iterator that goes over the grading script, problem solution files and grader libs
  class _grader_files_iterator:
  
    def __init__(self, problem):
      self.problem = problem
  
    def __iter__(self):
      return self

    def next(self):
      yield self.problem.grade_script
      for psfile in self.problemsolutionfile_set.all():
        yield psfile.file_upload
      for lib in GraderLib.objects.all():
        yield lib.lib_upload
      
      raise StopIteration()"""
  

class ProblemSolutionFile(models.Model):
  problem = models.ForeignKey(Problem, null=True)
  file_upload = models.FileField(upload_to=solution_file_upload_path)
  comment = models.CharField(max_length=200, null=True, blank=True)

class RequiredProblemFilename(models.Model):
  file_title = models.CharField(max_length=200)
  problem = models.ForeignKey(Problem, null=True)
  force_rename = models.BooleanField(default=True)
  #add field for extension
  def __str__(self):
    return self.file_title

"""
  def clean(self): #the other idea for making sure one of the student files is renamed; doesn't work
    if self.problem != None and not self.problem.one_force_rename:
      if self.force_rename:
        self.problem.one_force_rename = True
      else:
        raise ValidationError("you need to rename")
"""
class ProblemSet(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField(default='')
  problems = models.ManyToManyField(Problem)
  cs_section = models.ManyToManyField('catalog.Section')
  pub_date = models.DateTimeField('date assigned')
  due_date = models.DateTimeField('date due')

  def is_already_due(self):
    return self.due_date < timezone.now()

  def clean(self):
    if self.due_date < self.pub_date:
      raise ValidationError({'pub_date': ["",], 'due_date' : ["Probelem Set cannot be due before it is assigned!",]})
  
  def __str__(self): 
    return self.title

class StudentProblemSet(models.Model):
  problem_set = models.ForeignKey(ProblemSet)
  user = models.ForeignKey('generic.CSUser', null=True)
  submitted = models.DateTimeField('date submitted', null=True)
  
  def all_submitted(self):
    for s_prob in self.studentproblemsolution_set.all():
      if not s_prob.submitted:
        return False
    return True
  
  def __str__(self): 
    return self.problem_set.title + " - " + self.user.username
    
class StudentProblemSolution(models.Model):
  problem = models.ForeignKey(Problem)
  student_problem_set = models.ForeignKey(StudentProblemSet, null=True)
  attempt_num = models.IntegerField(default=0)
  submitted = models.DateTimeField('date submitted', null=True)

  #tango jobid
  job_id = models.IntegerField(default=-1)
  
  def __str__(self): 
    return self.problem.title + " - " + self.student_problem_set.user.username

  def is_late(self):
    ps_due_date = self.student_problem_set.problem_set.due_date
    submit_date = self.submitted
    if submit_date > ps_due_date:
      return 1
    else:
      return 0
  
class StudentProblemFile(models.Model):
  required_problem_filename = models.ForeignKey(RequiredProblemFilename, null=True)
  student_problem_solution = models.ForeignKey(StudentProblemSolution, null=True)
  submitted_file = models.FileField(upload_to=student_file_upload_path)
  attempt_num = models.IntegerField(default=0)

class ProblemResult(models.Model):
  #tango jobid
  job_id = models.IntegerField(default=-1)

  sp_sol = models.ForeignKey(StudentProblemSolution)
  problem = models.ForeignKey(Problem)
  sp_set = models.ForeignKey(StudentProblemSet, null=True)
  user = models.ForeignKey('generic.CSUser', null=True)

  #general data about the actual results
  timestamp = models.DateTimeField('date received', null=True, editable=False)
  score = models.IntegerField(default=-1)
  json_log = JSONField(null=True, blank=True)
  raw_output = models.TextField(null=True, blank=True)

  def external_log(self):
    return self.json_log["external_log"]

  def internal_log(self):
    return self.json_log["internal_log"]

  def sanity_log(self):
    return self.json_log["sanity_compare"]

#for testrunner files like session.py or sanity.py
class GraderLib(models.Model):
  lib_upload = models.FileField(upload_to=grader_lib_upload_path)
  comment = models.CharField(max_length=200, null=True, blank=True)
  
  def save(self, *args, **kwargs):
    super(GraderLib, self).save(*args, **kwargs)
    name = self.lib_upload.name.split("/")[-1]
    f = self.lib_upload.read()
    for ps in ProblemSet.objects.all():
      for problem in ps.problems.all().filter(autograde_problem=True):
        tango.upload(problem, ps, name, f)
  """
  def delete(self):
    os.remove(self.lib_upload.name)
    name = self.lib_upload.name.split("/")[-1]
    for ps in ProblemSet.objects.all():
      for problem in ps.problems.all():
        tango.delete(problem, ps, name)
    super(GraderLib, self).delete()
"""

  def __str__(self):
    return self.lib_upload.name.split("/")[-1]

