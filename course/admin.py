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

# admin.site.register(Problem)
# admin.site.register(ProblemSet)

# class ProblemSolutionInline(admin.TabularInline):
#   model = ProblemSolution
#   extra = 1

class RequiredProblemFilenameInline(admin.TabularInline):
  model = models.RequiredProblemFilename
  extra = 3


class ProblemSolutionFileInline(admin.TabularInline):
  model = models.ProblemSolutionFile
  extra = 3

#class StudentProblemSetInline(admin.StackedInline):
#  model = models.StudentProblemSet
#  show_change_link = True


# class ProblemSolutionAdmin(admin.ModelAdmin):
#   class Meta:
#     model = ProblemSolution
    
#   inlines = [ProblemSolutionFileInline]


class ProblemAdmin(admin.ModelAdmin):
  class Meta:
    model = models.Problem

  fieldsets = [
    ('Problem Info', {'fields': ['title', 'description', 'statement', 'many_attempts']}),
    # ('Required Files', {'fields': ['problem_files']}),
    ('Course Info', {'fields': ['course']}),
  ]
  inlines = [RequiredProblemFilenameInline, ProblemSolutionFileInline]
  list_display = ('title', 'course')

# class ProblemInline(admin.StackedInline):
#   model = Problem
#   extra = 1


class ProblemSetAdmin(admin.ModelAdmin):
  fieldsets = [
    ('Problem Set Info', {'fields': ['title', 'description']}),
    ('Problems', {'fields':['problems']}),
    ('Release & Due Dates', {'fields': ['pub_date', 'due_date']}),
  ]
  #inlines = [StudentProblemSetInline]
  list_display = ('title', 'pub_date', 'due_date')
  
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
    #open (make) the courselab on tango server with the callback _upload_ps_files
    url = vrfy.settings.TANGO_ADDRESS + "open/" + vrfy.settings.TANGO_KEY + "/" + slugify(obj.title) + "/"
    r = requests.get(url)
    
    #upload the files
    url = vrfy.settings.TANGO_ADDRESS + "upload/" + vrfy.settings.TANGO_KEY + "/" + slugify(obj.title) + "/"
    for problem in obj.problems.all():
      for psfile in models.ProblemSolutionFile.objects.filter(problem=problem):
        f = psfile.file_upload
        header = {'Filename': f.name.split("/")[-1]}
        r = requests.post(url, data=f.read(), headers=header)

# admin.site.register(RequiredProblemFilename, RequiredProblemFilenameAdmin)
# admin.site.register(ProblemSolution, ProblemSolutionAdmin)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.ProblemSet, ProblemSetAdmin)
admin.site.register(models.StudentProblemSet)
admin.site.register(models.StudentProblemSolution)
admin.site.register(models.StudentProblemFile)
