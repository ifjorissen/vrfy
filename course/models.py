from django.db import models
# from generic.models import CSUser
from catalog.models import Section, Course, Reedie
# from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.files import File
from jsonfield import JSONField
import os
import os.path
import vrfy.settings
from django.utils import timezone
from util import tango, pretty_code

def student_file_upload_path(instance, filename):
  #filepath should be of the form: course/folio/user/problem_set/problem/filename  (maybe add attempt number)
  problem_set = instance.student_problem_solution.student_problem_set.problem_set.title
  user = instance.student_problem_solution.student_problem_set.user.username()
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
  cs_course = models.ForeignKey('catalog.Course', null=True, verbose_name="Course Name")
  description = models.TextField(default='', help_text="You can use plain text, markdown, or html for your problem description") #markdown compatible
  statement = models.TextField(default='', verbose_name='TL;DR') #short statement, optional(?)
  many_attempts = models.BooleanField(default=True, verbose_name="allow multiple attempts")
  autograde_problem = models.BooleanField(default=True, verbose_name="autograde this problem")
  grade_script = models.FileField(upload_to=grade_script_upload_path, null=True, blank=True, help_text="Upload the script that grades the student submission here")
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
  file_upload = models.FileField(upload_to=solution_file_upload_path, help_text="Upload a solution file here")
  comment = models.CharField(max_length=200, null=True, blank=True)

  def __str__(self):
    return self.file_upload.name.split("/")[-1]

class RequiredProblemFilename(models.Model):
  file_title = models.CharField(max_length=200, help_text="Use the name of the python file the grader script imports as a module. E.g: main.py if the script imports main")
  problem = models.ForeignKey(Problem, null=True)
  force_rename = models.BooleanField(default=True, help_text="Uncheck if file name does not matter")
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
  description = models.TextField(default='', help_text="Provide some additional information about this problem set.")
  problems = models.ManyToManyField(Problem)
  cs_section = models.ManyToManyField('catalog.Section', verbose_name="course Section")
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
  # user = models.ForeignKey('generic.CSUser', null=True)
  # user = models.ForeignKey(User)
  user = models.ForeignKey('catalog.Reedie')
  submitted = models.DateTimeField('date submitted')

  def problems_completed(self):
    solutions = self.studentproblemsolution_set.all()
    problems = self.problem_set.problems.all()
    return "{!r} of {!r}".format(len(solutions), len(problems))
  
  def all_submitted(self):
    problems = self.problem_set.problems.all()
    solutions = self.studentproblemsolution_set.all()
    if len(problems) == len(solutions):
      return True
    else:
      return False
  
  def __str__(self): 
    return self.problem_set.title + " - " + self.user.username()
    
class StudentProblemSolution(models.Model):
  problem = models.ForeignKey(Problem)
  student_problem_set = models.ForeignKey(StudentProblemSet, null=True)
  attempt_num = models.IntegerField(default=0, verbose_name='attempts made')
  submitted = models.DateTimeField('date submitted', null=True)

  #tango jobid
  job_id = models.IntegerField(default=-1, verbose_name="Tango Job ID")
  
  def __str__(self): 
    return self.problem.title + " - " + self.student_problem_set.user.username()

  def is_late(self):
    ps_due_date = self.student_problem_set.problem_set.due_date
    submit_date = self.submitted
    if submit_date == None:
      return 0
    if submit_date > ps_due_date:
      return 1
    else:
      return 0

  def get_user(self):
    return self.student_problem_set.user
  get_user.short_description = "user"

  def get_problemset(self):
    return self.student_problem_set.problem_set
  get_problemset.short_description = "Problem Set"

  def get_max_score(self):
    result_obj = self.problemresult_set.get(attempt_num=self.attempt_num)
    max_score = result_obj.get_max_score()
    return max_score


  def latest_score(self):
    result_obj = self.problemresult_set.get(attempt_num=self.attempt_num)
    score = result_obj.get_score()
    return score

  def submitted_code_table(self):
    attempt = self.attempt_num
    files = self.studentproblemfile_set.get(attempt_num=attempt)
    #get file content (assumes only one file submission)
    submission = File(files.submitted_file)
    code = submission.read()
    submission.close()
    code = pretty_code.python_prettify(code, "table")
    return code

  submitted_code_table.short_description = "Submitted Code"

  def submitted_code(self):
    attempt = self.attempt_num
    files = self.studentproblemfile_set.get(attempt_num=attempt)
    #get file content (assumes only one file submission)
    submission = File(files.submitted_file)
    code = submission.read()
    submission.close()
    code = pretty_code.python_prettify(code, "inline")
    return code

  def cs_section(self):
    user = self.get_user()
    cs_sections = self.get_problemset().cs_section.all()
    section = set(user.enrolled.all()).intersection(cs_sections)
    return section.pop()
  
class StudentProblemFile(models.Model):
  required_problem_filename = models.ForeignKey(RequiredProblemFilename, null=True)
  student_problem_solution = models.ForeignKey(StudentProblemSolution, null=True)
  submitted_file = models.FileField(upload_to=student_file_upload_path)
  attempt_num = models.IntegerField(default=0)

  def __str__(self):
    head, filename = os.path.split(self.submitted_file.name)
    return filename

class ProblemResult(models.Model):
  #tango jobid
  job_id = models.IntegerField(default=-1, verbose_name="Tango Job ID")
  attempt_num = models.IntegerField(default=-1)
  sp_sol = models.ForeignKey(StudentProblemSolution, verbose_name="Student Problem Solution")
  problem = models.ForeignKey(Problem)
  sp_set = models.ForeignKey(StudentProblemSet, verbose_name="Student Problem Set")
  user = models.ForeignKey('catalog.Reedie')

  #general data about the actual results
  timestamp = models.DateTimeField('date received', null=True) #, editable=False)
  max_score = models.IntegerField(blank=True, null=True)
  score = models.IntegerField(default=-1)
  json_log = JSONField(null=True, blank=True, verbose_name="Session Log")
  raw_output = models.TextField(null=True, blank=True, verbose_name="Raw Autograder Output")

  def external_log(self):
    return self.json_log["external_log"]

  def internal_log(self):
    return self.json_log["internal_log"]

  def sanity_log(self):
    return self.json_log["sanity_compare"]

  def get_score(self):
    if self.problem.autograde_problem:
      return self.score
    else:
      return "Not Autograded"

  def get_max_score(self):
    if self.problem.autograde_problem:
      return self.max_score
    else:
      return None

  def __str__(self):
    return self.problem.title + "_" + self.user.username()+"_jobID" + str(self.job_id)

#for testrunner files like session.py or sanity.py
class GraderLib(models.Model):
  lib_upload = models.FileField(upload_to=grader_lib_upload_path, verbose_name="Grader Resource")
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

