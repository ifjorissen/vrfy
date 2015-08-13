import csv
from zipfile import ZipFile
from django.contrib import admin
from django.utils.text import slugify
from django.http import Http404, HttpResponse
from . import models
import requests
import shutil
import os
import json
from django.core.files import File
from django.core.servers.basehttp import FileWrapper
import datetime
import sys
sys.path.append("../")
import vrfy.settings
from util import tango
# from django.core import serializers

admin.site.site_header = "Homework Administration"
admin.site.site_title = "Homework Administration"

#Inlines
class RequiredProblemFilenameInline(admin.TabularInline):
  model = models.RequiredProblemFilename
  extra = 2

class ProblemSolutionFileInline(admin.TabularInline):
  model = models.ProblemSolutionFile
  extra = 3
  fields = ['file_upload', 'comment']

class StudentProblemSetInline(admin.TabularInline):
  readonly_fields = ('user', 'submitted')
  model = models.StudentProblemSet
  extra = 0
  show_change_link = True

class StudentProblemSolutionInline(admin.TabularInline):
  can_delete = False
  readonly_fields = ('problem', 'submitted', 'student_problem_set', 'attempt_num', 'job_id')
  model = models.StudentProblemSolution
  extra = 0
  show_change_link = True

class StudentProblemFileInline(admin.TabularInline):
  can_delete = False
  readonly_fields = ('required_problem_filename',  'submitted_file')
  exclude = ('attempt_num',)
  model = models.StudentProblemFile
  extra = 0

# class ProblemResultInline(admin.StackedInline):
#   # show_change_link = True
#   fieldsets = [
#    ('Result Info', {'fields': ('timestamp', 'score', 'json_log')}),
#    ('Raw Autograder Output', {'classes':('grp-collapse grp-open',), 'fields': ('raw_output',)}),
#   ]
#   model = models.ProblemResult
#   extra = 0

@admin.register(models.Problem)
class ProblemAdmin(admin.ModelAdmin):
  class Meta:
    model = models.Problem

  fieldsets = [
    ('Problem Info', {'fields': ['title', 'description', 'statement', 'many_attempts', 'autograde_problem', 'cs_course']}),
    ('Grading Script', {'fields': ['grade_script']}),
  ]
  inlines = [RequiredProblemFilenameInline, ProblemSolutionFileInline]
  list_display = ('title', 'cs_course', 'assigned_to', 'submissions')
  list_filter = ('cs_course',)

  def assigned_to(self, obj):
    problem_sets = obj.problemset_set.all()
    return ", ".join([ps.title for ps in problem_sets]) 

  def submissions(self, obj):
    student_solutions = obj.studentproblemsolution_set.all()
    return len(student_solutions)

  def get_readonly_fields(self, request, obj=None):
    if obj: # obj is not None, so this is an edit
        return ['title',]
    else: # This is an addition
        return []

  def response_change(self, request, obj):
    """
    upload files to Tango
    I only need to do this when a problem is changed, because when a problem is added, it doesn't have a problem set yet
    """
    if obj.autograde_problem:
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

@admin.register(models.ProblemSet)
class ProblemSetAdmin(admin.ModelAdmin):
  fieldsets = [
    ('Problem Set Info', {'fields': ['title', 'description']}),
    ('Sections', {'fields':['cs_section']}),
    ('Problems', {"classes": ('grp-collapse grp-open',), 'fields':['problems']}),
    ('Release & Due Dates', {'fields': ['pub_date', 'due_date']}),
  ]

  filter_vertical = ['problems']
  # inlines = [StudentProblemSetInline]
  list_display = ('title', 'cs_sections', 'pub_date', 'due_date', 'problems_included', 'submissions')
  list_filter = ('cs_section',)


  def cs_sections(self, obj):
    return ", ".join([str(section) for section in obj.cs_section.all()]) 
 
  def submissions(self, obj):
    student_solutions = obj.studentproblemset_set.all()
    return len(student_solutions)

  def problems_included(self, obj):
    return ", ".join([problem.title for problem in obj.problems.all()])    
  
  def get_readonly_fields(self, request, obj=None):
    if obj: # obj is not None, so this is an edit
        return ['title',]
    else: # This is an addition
        return []
  
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
    for problem in obj.problems.all().filter(autograde_problem=True):
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

@admin.register(models.StudentProblemSet)
class StudentProblemSetAdmin(admin.ModelAdmin):
  readonly_fields = ('problem_set', 'user', 'submitted')
  inlines = [StudentProblemSolutionInline]
  list_display = ('problem_set','cs_sections', 'user','submitted', 'date_due', 'problems_completed',)
  list_filter = ('user', 'problem_set')

  def cs_sections(self, obj):
    return ", ".join([str(section) for section in obj.problem_set.cs_section.all()])  

  def date_due(self, obj):
    return obj.problem_set.due_date


@admin.register(models.StudentProblemSolution)
class StudentProblemSolutionAdmin(admin.ModelAdmin):
  actions = ['export_csv', 'export_files']
  class Media:
    css = {
        "all": ("course/css/pygments.css",)
    }

  can_delete = False
  exclude = ('job_id',)
  readonly_fields = ('problem', 'job_id', 'attempt_num', 'submitted', 'cs_section', 'get_user', 'get_problemset', 'result_json', 'result_raw_output', 'submitted_code_table','latest_score', 'late')
  fieldsets = [
    ('Solution Info', {'classes':('grp-collapse grp-open',), 'fields': ('problem', 'get_problemset', 'latest_score', 'get_user',)}),
    ('Solution Detail', {'classes':('grp-collapse grp-open',), 'fields': ('cs_section', 'attempt_num', 'submitted', 'late', 'job_id',)}),
    ('Most Recent Result', {'classes':('grp-collapse grp-open',), 'fields': (('submitted_code_table','result_json'), 'result_raw_output',)}),
  ]

  # inlines = [StudentProblemFileInline]
  list_display = ('problem', 'cs_section', 'get_user', 'get_problemset', 'attempt_num', 'submitted', 'latest_score', 'late')
  list_filter = ('student_problem_set__user__user__username', 'student_problem_set__problem_set', 'problem')
  # search_fields = ('student_problem_set__user__username',)

  def export_csv(self, request, queryset):
    date = datetime.datetime.now()
    filename = "studentsolutions-{}".format(date.strftime("%d_%m_%y"))
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
    writer = csv.writer(response)
    writer.writerow(['Problem Name', 'Problem Set', 'Course:Section', 'Attempts Made', 'Latest Score', 'User', 'Submitted On', 'Late'])
    for obj in queryset:
      writer.writerow([obj.problem, obj.get_problemset(), obj.cs_section(), obj.attempt_num, obj.latest_score(), obj.get_user(), obj.submitted, self.late(obj)])
    return response
  
  export_csv.short_description = "Export Selected to CSV"

  #send the files to a zip
  def export_files(self, request, queryset):
    
    with ZipFile('StudentSolutions.zip', 'w') as sols_zip:
      for obj in queryset:
      
        prob = slugify(obj.problem)
        ps = slugify(obj.get_problemset())
        user = str(obj.get_user())
        
        for psfile in obj.studentproblemfile_set.filter(attempt_num=obj.attempt_num):
          head, filename = os.path.split(psfile.submitted_file.name)
          path = os.path.join(vrfy.settings.MEDIA_ROOT, psfile.submitted_file.name)
          sols_zip.write(path, "{!s}/{!s}/{!s}/{!s}".format(ps, prob, user, filename),  )
  
    #probably inefficient to write a file to disk just to read it again
    #TODO: change to an in-mememory solution
    with open('StudentSolutions.zip', 'rb') as sols_zip:
      response = HttpResponse(FileWrapper(sols_zip), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=StudentSolutions.zip'
    return response

  def result_json(self, obj):
    result = obj.problemresult_set.get(job_id=obj.job_id)
    return json.dumps(result.json_log, indent=2)

  def result_raw_output(self, obj):
    result = obj.problemresult_set.get(job_id=obj.job_id)
    return result.raw_output

  # def problem_set(self, obj):
  #   return obj.student_problem_set.problem_set
  # def cs_sections(self, obj):
  #   return ", ".join([str(section) for section in obj.student_problem_set.problem_set.cs_section.all()])  

  def late(self, obj):
    if obj.is_late():
      return 'Yes'
    else:
      return 'No'

@admin.register(models.GraderLib)
class GraderLibAdmin(admin.ModelAdmin):
  #readonly_fields=('lib_upload',)
  fields = ('lib_upload', 'comment')

  def get_readonly_fields(self, request, obj=None):
    if obj: # obj is not None, so this is an edit
        return ['lib_upload',] # Return a list or tuple of readonly fields' names
    else: # This is an addition
        return []

@admin.register(models.ProblemResult)
class ProblemResultAdmin(admin.ModelAdmin):
  readonly_fields = ('cs_sections', 'problem', 'problem_set', 'user', 'score', 'attempt_num', 'late', 'timestamp', 'session_log', 'raw_output', 'job_id')
  fieldsets = [
    ('Problem Info', {'classes':('grp-collapse grp-open',), 'fields': ('problem', 'problem_set', 'cs_sections', 'user', 'timestamp', 'job_id')}),
    ('Result Info', {'classes':('grp-collapse grp-open',), 'fields': ('score', 'attempt_num', 'late', 'session_log',)}),
    ('Raw Autograder Output', {'classes':('grp-collapse grp-closed',), 'fields': ('raw_output',)}),
  ]
  list_display = ('problem', 'problem_set', 'cs_sections', 'user', 'attempt_num', 'late', 'score', 'timestamp')
  list_filter = ('user', 'problem')

  def cs_sections(self, obj):
    return ", ".join([str(section) for section in obj.sp_set.problem_set.cs_section.all()])  

  def late(self, obj):
    if obj.sp_sol.submitted is not None:
      if obj.sp_sol.is_late():
        return 'Yes'
      else:
        return 'No'
    else:
      return 'N/A'

  def problem_set(self, obj):
    return obj.sp_set.problem_set.title

  def session_log(self, obj):
    log = json.dumps(obj.json_log, sort_keys=True, indent=2)
    return log
