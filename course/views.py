from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils import timezone
from django.utils.text import slugify
from .models import ProblemSet, ProblemSolutionFile
from generic.views import *
from generic.models import CSUser
import requests
import json

import sys
sys.path.append("../")
import vrfy.settings

from django.forms.models import inlineformset_factory


def index(request):
  authenticate(request)
  return render(request, 'course/index.html')

def attempt_problem_set(request, ps_id):
  authenticate(request)
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
  
  response = "here's that problem set: {!s} you clicked on".format(ps_id)
  return render(request, 'course/attempt_problem_set.html', {'problem_set': ps})

def problem_set_index(request):
  authenticate(request)
  latest_problem_sets = ProblemSet.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')
  context = {'latest_problem_sets': latest_problem_sets}
  return render(request, 'course/problem_set_index.html', context)

def problem_set_detail(request, ps_id):
  authenticate(request)
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())

  response = "here's that problem set: {!s} you clicked on".format(ps_id)
  return render(request, 'course/problem_set_detail.html', {'problem_set': ps})

#for submitting files
def problem_set_submit(request, ps_id):
  authenticate(request)

  if request.method == 'POST':#make sure the user doesn't type this into the address bar
    ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
    
    #opens the courselab
    url = vrfy.settings.TANGO_ADDRESS + "upload/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title) + "/"
    files = []
    #getting all the submitted files
    for name, f in request.FILES.items():
      localfile = name + "-"+ request.user.username
      header = {'Filename': localfile}
      r = requests.post(url, data=f.read(), headers=header)
      files.append({"localFile" : localfile, "destFile":name})#for the addJob command
    
    #getting all the grader files
    for problem in ps.problems.all():
      for psfile in ProblemSolutionFile.objects.filter(problem=problem):
        name = psfile.file_upload.name.split("/")[-1]
        if "makefile" in name.lower():#if makefile is in the name, designate it as THE makefile
          files.append({"localFile" : name, "destFile": "Makefile"})
        else:
          files.append({"localFile" : name, "destFile": name})

    #making Tango run the files
    jobname = slugify(ps.title) + "-" + request.user.username
    body = json.dumps({"image": "autograding_image", "files": files, "jobName": jobname, "output_file": jobname,"timeout": 1000})
    #raise Http404(body)
    url = vrfy.settings.TANGO_ADDRESS + "addJob/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title) + "/"
    r = requests.post(url, data=body)
    
    return HttpResponseRedirect("/results/" + ps_id + "/")
    
  else:
    raise Http404("Don't do that")

#submission & files urls; summary of a problem set & files submitted
#ability to view each attempt and the files submitted with each attempt

#returns the results of a given problem set (and all attempts)
def results_detail(request, ps_id):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
  
  #poll the tango server
  url = vrfy.settings.TANGO_ADDRESS + "poll/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title) + "/" + slugify(ps.title) + "-" + request.user.username + "/"
  r = requests.get(url)
  
  context = {'output': r.text}
  return render(request, 'course/results_detail.html', context)
  # return HttpResponse("And Here are the results for one your problem sets")

def results_index(request):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  response = "here are all the results that are availiable"
  return render(request, 'course/results_index.html')
  # return HttpResponse("And Here are the results for your problem sets")

"""
# problem set id, problem id
def add_student_solution_files(request, ps_id, p_id):
  problem_set = ProblemSet.objects.get(pk=ps_id)

  for problem in problem_set.problems:
    SSFileInlineFormSet = inlineformset_factory(StudentProblemSolution, StudentProblemFile, fields=('file_title'))

    # author = Author.objects.get(pk=author_id)
    # BookInlineFormSet = inlineformset_factory(Author, Book, fields=('title',))
    if request.method == "POST":
        formset = SSFileInlineFormSet(request.POST, request.FILES, instance=problem)
        if formset.is_valid():
            formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(author.get_absolute_url())
    else:
        formset = SSFileInlineFormSet(instance=problem)

    return render_to_response("manage_books.html", {
        "formset": formset,
    })
"""
