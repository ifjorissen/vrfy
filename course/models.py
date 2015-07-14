from django.db import models
from generic.models import CSUser
from django.contrib.auth.models import User
from django.utils.text import slugify
import os

# A problem model, which requires:
# a problem title 
# a class associated with the problem
# and a problem description
# To do: potentially make the class a tag instead
# boolean = assigned or not assigned (should remove??)
# problem set it's assoicated with
# each problem points to a set of user submitted solutions
# as well as a summary of results 

def student_file_upload_path(instance, filename):
  #filepath should be of the form: course/folio/user/problem_set/problem/filename  (maybe add attempt number)
  problem_set = instance.student_problem_solution.student_problem_set.problem_set.title
  user = instance.student_problem_solution.student_problem_set.user.username
  problem = instance.student_problem_solution.problem
  attempt = instance.attempt_num
  course = problem.course
  return '{0}/folio/{1}/{2}/{3}_files/v{4}/{5}'.format(course, user, slugify(problem_set), slugify(problem.title), attempt, slugify(filename))

def solution_file_upload_path(instance, filename):
  #filepath should be of the form: course/solutions/problem_set/problem/filename 
  problem = instance.problem
  course = problem.course
  file_path = '{0}/solutions/{1}_files/{2}'.format(slugify(course), slugify(problem.title), filename)
  #remove the old file
  try:
    os.remove(file_path)
  except OSError:
      pass
  return file_path

def grade_script_upload_path(instance, filename):
  #filepath should be of the form: course/solutions/problem_set/problem/filename 
  title = instance.title
  course = instance.course
  file_path = '{0}/solutions/{1}_files/{2}'.format(slugify(course), slugify(title), filename)
  #remove the old file
  try:
    os.remove(file_path)
  except OSError:
      pass
  return file_path

class Problem(models.Model):
  # title default could be problem id
  title = models.CharField(max_length=200)
  course = models.CharField(max_length=200)
  description = models.TextField(default='') #a short tl;dr of the problem, what to read
  statement = models.TextField(default='') #markdown compatible
  many_attempts = models.BooleanField(default = True)
  grade_script = models.FileField(upload_to=grade_script_upload_path)
  # slug = models.SlugField(max_length = 60, unique = True, default='')

  def __str__(self): 
    return self.title

class ProblemSolutionFile(models.Model):
  # file_title = models.CharField(max_length=200)
  problem = models.ForeignKey(Problem, null=True)
  file_upload = models.FileField(upload_to=solution_file_upload_path)
  comment = models.CharField(max_length=200, null=True, blank=True)

class RequiredProblemFilename(models.Model):
  file_title = models.CharField(max_length=200)
  problem = models.ForeignKey(Problem, null=True)
  #add field for extension
  def __str__(self):
    return self.file_title

class ProblemSet(models.Model):
  title = models.CharField(max_length=200)
  description = models.TextField(default='')
  problems = models.ManyToManyField(Problem)
  # ps_slug = models.SlugField(max_length = 60, unique = True, default='')
  # submissions = models.IntegerField('number of submissions', default = 0)
  # solutions = models.ManyToManyField(ProblemSolution)
  pub_date = models.DateTimeField('date assigned')
  due_date = models.DateTimeField('date due')

  def __str__(self): 
    return self.title

class StudentProblemSet(models.Model):
  problem_set = models.ForeignKey(ProblemSet)
  user = models.ForeignKey('generic.CSUser', null=True)
  submitted = models.DateTimeField('date submitted', null=True)
  # comments = models.TextField(), 

  def __str__(self): 
    return self.problem_set.title + " - " + self.user.username
    
#this has not been tested at all
#should also use student forms probably: https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/#django.forms.ModelForm
class StudentProblemSolution(models.Model):
  #email field to email users when result is ready
  problem = models.ForeignKey(Problem)
  student_problem_set = models.ForeignKey(StudentProblemSet, null=True)
  attempt_num = models.IntegerField(default=0)
  submitted = models.DateTimeField('date submitted', null=True)
  # submitted_files = models.ManyToManyField(StudentProblemFile)
  # files = models.ManyToManyField()
  #date time
  #submitted files
  
  def __str__(self): 
    return self.problem.title + " - " + self.student_problem_set.user.username
  
class StudentProblemFile(models.Model):
  required_problem_filename = models.ForeignKey(RequiredProblemFilename, null=True)
  student_problem_solution = models.ForeignKey(StudentProblemSolution, null=True)
  # potentially could automatically upload to afs
  submitted_file = models.FileField(upload_to=student_file_upload_path)
  attempt_num = models.IntegerField(default=0)



#ability for jim to access something on the order of /m121/folio/jfix/hw1/p1/v1/files/  and /m121/folio/jfix/hw1/p1/v1/files/
#a csv with output for the latest (or best) attempt on the problem set
