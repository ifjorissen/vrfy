from django.contrib import admin
from django.utils.text import slugify
from django.http import Http404
from . import models #Problem, ProblemSet, RequiredProblemFilename, ProblemSolutionFile
import requests
import shutil

import sys
sys.path.append("../")
import vrfy.settings

admin.site.site_header = "Homework Administration"
admin.site.site_title = "Homework Administration"

class RequiredProblemFilenameInline(admin.TabularInline):
  model = models.RequiredProblemFilename
  extra = 2


class ProblemSolutionFileInline(admin.TabularInline):
  model = models.ProblemSolutionFile
  extra = 5

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


# class ProblemSolutionAdmin(admin.ModelAdmin):
#   class Meta:
#     model = ProblemSolution
    
#   inlines = [ProblemSolutionFileInline]


class ProblemAdmin(admin.ModelAdmin):
  class Meta:
    model = models.Problem

  fieldsets = [
    ('Problem Info', {'fields': ['title', 'description', 'statement', 'many_attempts', 'course']}),
    ('Grading Script', {'fields': ['grade_script']}),
  ]
  inlines = [RequiredProblemFilenameInline, ProblemSolutionFileInline]
  list_display = ('title', 'course', 'submissions')

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
    shutil.rmtree(vrfy.settings.TANGO_COURSELAB_DIR + vrfy.settings.TANGO_KEY + "-" + slugify(obj_display))
    return super(ProblemSetAdmin, self).response_delete(request, obj_display, obj_id)

  def _open_and_upload(self, obj):
    """
    Helper function that gets called for response change and response add
    It opens a new courselab and then uploads the grading files
    """
    for problem in obj.problems.all():
      #open (make) the courselab on tango server with the callback _upload_ps_files
      open_url = vrfy.settings.TANGO_ADDRESS + "open/" + vrfy.settings.TANGO_KEY + "/" + slugify(obj.title) + "_" + \
      slugify(problem.title) + "/" 
      r = requests.get(open_url)
      
      #upload the files
      upload_url = vrfy.settings.TANGO_ADDRESS + "upload/" + vrfy.settings.TANGO_KEY + "/" + slugify(obj.title) + "_" + \
      slugify(problem.title) + "/"

      #upload the grader librarires
      for lib in models.GraderLib.objects.all():
        f = lib.lib_upload
        header = {'Filename': f.name.split("/")[-1]}
        r = requests.post(upload_url, data=f.read(), headers=header)

      #upload the grading script
      grading = problem.grade_script
      grading_name = grading.name.split("/")[-1]
      header = {'Filename': grading_name}
      r = requests.post(upload_url, data=grading.read(), headers=header)

      #upload the makefile that will run the grading script
      header = {'Filename': "autograde-Makefile"}
      makefile = 'autograde:\n	@python3 ' + grading_name
      r = requests.post(upload_url, data=makefile, headers=header)

      #upload all the other files
      for psfile in models.ProblemSolutionFile.objects.filter(problem=problem):
        f = psfile.file_upload
        header = {'Filename': f.name.split("/")[-1]}
        r = requests.post(upload_url, data=f.read(), headers=header)

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



admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.ProblemSet, ProblemSetAdmin)
admin.site.register(models.StudentProblemSet, StudentProblemSetAdmin)
admin.site.register(models.StudentProblemSolution, StudentProblemSolutionAdmin)
admin.site.register(models.GraderLib)
