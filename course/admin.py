from django.contrib import admin
from django.utils.text import slugify
from django.http import Http404
from . import models #Problem, ProblemSet, RequiredProblemFilename, ProblemSolutionFile
import requests
import shutil
import os

import sys
sys.path.append("../")
import vrfy.settings
from util import tango

admin.site.site_header = "Homework Administration"
admin.site.site_title = "Homework Administration"

class RequiredProblemFilenameInline(admin.TabularInline):
  model = models.RequiredProblemFilename
  extra = 2


class ProblemSolutionFileInline(admin.TabularInline):
  model = models.ProblemSolutionFile
  extra = 3

class StudentProblemSetInline(admin.TabularInline):
  model = models.StudentProblemSet
  extra = 0
  show_change_link = True

class StudentProblemSolutionInline(admin.TabularInline):
  model = models.StudentProblemSolution
  extra = 0
  show_change_link = True

class StudentProblemFileInline(admin.TabularInline):
  model = models.StudentProblemFile
  extra = 0

class ProblemAdmin(admin.ModelAdmin):
  class Meta:
    model = models.Problem

  fieldsets = [
    ('Problem Info', {'fields': ['title', 'description', 'statement', 'many_attempts', 'autograde_problem', 'cs_course']}),
    ('Grading Script', {'fields': ['grade_script']}),
  ]
  inlines = [RequiredProblemFilenameInline, ProblemSolutionFileInline]
  list_display = ('title', 'cs_course', 'submissions', 'assigned_to')

  def assigned_to(self, obj):
    problem_sets = obj.problemset_set.all()
    return ", ".join([ps.title for ps in problem_sets]) 

  def response_change(self, request, obj):
    """
    upload files to Tango
    I only need to do this when a problem is changed, because when a problem is added, it doesn't have a problem set yet
    """
    for ps in obj.problemset_set.all():

      #upload the grading script
      grading = obj.grade_script
      grading_name = grading.name.split("/")[-1]
      tango.upload(obj, ps, grading_name, grading.read())

      #upload the makefile that will run the grading script
      makefile = 'autograde:\n	@python3 ' + grading_name
      tango.upload(obj, ps, vrfy.settings.MAKEFILE_NAME, makefile)
      
      #upload problemsolutionfiles
      for psfile in models.ProblemSolutionFile.objects.filter(problem=obj):
        f = psfile.file_upload
        tango.upload(obj, ps, f.name.split("/")[-1], f.read())
    
    return super(ProblemAdmin, self).response_change(request, obj)

  def submissions(self, obj):
    student_solutions = obj.studentproblemsolution_set.all()
    return len(student_solutions)


class ProblemSetAdmin(admin.ModelAdmin):
  fieldsets = [
    ('Problem Set Info', {'fields': ['title', 'description']}),
    ('Problems', {'fields':['problems']}),
    ('Release & Due Dates', {'fields': ['pub_date', 'due_date']}),
  ]
  filter_vertical = ['problems']
  inlines = [StudentProblemSetInline]
  list_display = ('title', 'pub_date', 'due_date', 'problems_included',)

  def problems_included(self, obj):
    return ", ".join([problem.title for problem in obj.problems.all()])    
  
  #add a courselab and files to Tango when Problem Set is added and saved for the first time
  def response_add(self, request, obj, post_url_continue=None):
    self._open_and_upload(obj)
    return super(ProblemSetAdmin, self).response_add(request, obj, post_url_continue=None)
        
  #reupload files to Tanfo when a Problem Set is changed and saved
  def response_change(self, request, obj):
    self._open_and_upload(obj)
    return super(ProblemSetAdmin, self).response_change(request, obj)

  def response_delete(self, request, obj_display, obj_id):
    
    return super(ProblemSetAdmin, self).response_delete(request, obj_display, obj_id)

  def _open_and_upload(self, obj):
    """
    Helper function that gets called for response change and response add
    It opens a new courselab and then uploads the grading files
    """
    for problem in obj.problems.all():
      #open (make) the courselab on tango server with the callback _upload_ps_files
      tango.open(problem, obj)
      
      #upload the grader librarires
      for lib in models.GraderLib.objects.all():
        f = lib.lib_upload
        tango.upload(problem, obj, f.name.split("/")[-1], f.read())

      #upload the grading script
      grading = problem.grade_script
      grading_name = grading.name.split("/")[-1]
      tango.upload(problem, obj, grading_name, grading.read())

      #upload the makefile that will run the grading script
      makefile = 'autograde:\n	@python3 ' + grading_name
      tango.upload(problem, obj, vrfy.settings.MAKEFILE_NAME, makefile)

      #upload all the other files
      for psfile in models.ProblemSolutionFile.objects.filter(problem=problem):
        f = psfile.file_upload
        tango.upload(problem, obj, f.name.split("/")[-1], f.read())

class StudentProblemSetAdmin(admin.ModelAdmin):
  inlines = [StudentProblemSolutionInline]
  list_display = ('problem_set','user','submitted',)

class StudentProblemSolutionAdmin(admin.ModelAdmin):
  inlines = [StudentProblemFileInline]
  list_display = ('problem', 'student_problem_set', 'attempt_num', 'submitted', 'latest_result')

  def get_user(self, obj):
    return obj.student_problem_set.user

  def latest_result(self, obj):
    result_obj = obj.problemresult_set.all().order_by('timestamp')[0]
    score = result_obj.score
    return score


class GraderLibAdmin(admin.ModelAdmin):
  
  def response_add(self, request, obj, post_url_continue=None):
    self._upload_to_ps(obj)
    return super(GraderLibAdmin, self).response_add(request, obj, post_url_continue=None)
        
  #reupload files to Tanfo when a Problem Set is changed and saved
  def response_change(self, request, obj):
    self._upload_to_ps(obj)
    return super(GraderLibAdmin, self).response_change(request, obj)
  
  def _upload_to_ps(self, obj):
    
    for ps in models.ProblemSet.objects.all():
      for problem in ps.problems.all():
        f = obj.lib_upload
        tango.upload(problem, ps, f.name.split("/")[-1], f.read())

class ProblemResultAdmin(admin.ModelAdmin):
  list_display = ('problem_title', 'problem_set', 'user', 'score', 'timestamp')

  def problem_set(self, obj):
    return obj.result_set.problem_set.title
    
  def problem_title(self, obj):
    return obj.problem.title


admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.ProblemSet, ProblemSetAdmin)
admin.site.register(models.StudentProblemSet, StudentProblemSetAdmin)
admin.site.register(models.StudentProblemSolution, StudentProblemSolutionAdmin)
admin.site.register(models.GraderLib, GraderLibAdmin)
admin.site.register(models.ProblemResultSet)
admin.site.register(models.ProblemResult, ProblemResultAdmin)
