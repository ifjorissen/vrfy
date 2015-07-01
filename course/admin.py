from django.contrib import admin
from django.utils.text import slugify
from django.http import Http404
from .models import Problem, ProblemSet, RequiredProblemFilename, ProblemSolutionFile
import requests

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
  model = RequiredProblemFilename
  extra = 3


class ProblemSolutionFileInline(admin.TabularInline):
  model = ProblemSolutionFile
  extra = 3


# class ProblemSolutionAdmin(admin.ModelAdmin):
#   class Meta:
#     model = ProblemSolution
    
#   inlines = [ProblemSolutionFileInline]


class ProblemAdmin(admin.ModelAdmin):
  class Meta:
    model = Problem

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
  # inlines = [ProblemInline]
  list_display = ('title', 'pub_date', 'due_date')
  
  #add a courselab and files to Tango when Problem Set is opened
  def save_model(self, request, obj, form, change):
    obj.save()

    #open the courselab
    url = vrfy.settings.TANGO_ADDRESS + "open/" + vrfy.settings.TANGO_KEY + "/" + slugify(obj.title) + "/"
    r = requests.get(url)
        
    #upload the files
    url = vrfy.settings.TANGO_ADDRESS + "upload/" + vrfy.settings.TANGO_KEY + "/" + slugify(obj.title) + "/"
    for problem in obj.problems.all():
      for psfile in ProblemSolutionFile.objects.filter(problem=problem):
        f = psfile.file_upload
        header = {'Filename': f.name.split("/")[-1]}
        r = requests.post(url, data=f.read(), headers=header)
    

# admin.site.register(RequiredProblemFilename, RequiredProblemFilenameAdmin)
# admin.site.register(ProblemSolution, ProblemSolutionAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(ProblemSet, ProblemSetAdmin)
