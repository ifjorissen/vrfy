from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils import timezone
from django.utils.text import slugify
from .models import *
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
  student_problemset_solutions = [StudentProblemSet.objects.filter(user=request.user, problem_set__id = ps.id) for ps in latest_problem_sets]
  print(request.user)
  print(student_problemset_solutions)
  print(StudentProblemSet.objects.filter(user=request.user))
  context = {'latest_problem_sets': latest_problem_sets}
  return render(request, 'course/problem_set_index.html', context)

def problem_set_detail(request, ps_id):
  authenticate(request)
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())

  response = "here's that problem set: {!s} you clicked on".format(ps_id)
  return render(request, 'course/problem_set_detail.html', {'problem_set': ps})

def problem_submit(request, p_id, ps_id):
  authenticate(request)
  if request.method == 'POST':#make sure the user doesn't type this into the address bar
    ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
    problem = get_object_or_404(Problem, pk=p_id)

    #create the student stuff
    student_ps_sol, sps_created = StudentProblemSet.objects.get_or_create( problem_set=ps, user=request.user, submitted=timezone.now())
    student_psol, s_created = StudentProblemSolution.objects.get_or_create(problem=problem, student_problem_set=student_ps_sol)
    
    #opens the courselab
    url = vrfy.settings.TANGO_ADDRESS + "upload/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title)+ "/"
    files = []

    #getting all the submitted files
    for name, f in request.FILES.items():
      localfile = name + "-"+ request.user.username
      header = {'Filename': localfile}
      r = requests.post(url, data=f.read(), headers=header)
      files.append({"localFile" : localfile, "destFile":name})#for the addJob command
      required_pf = RequiredProblemFilename(pk=p_id, file_title=name)
      print(required_pf)
      prob_file, pf_created = StudentProblemFile.objects.get_or_create(required_problem_filename=required_pf, student_problem_solution = student_psol, submitted_file=f)
    
    #getting all the grader files
    for psfile in ProblemSolutionFile.objects.filter(problem=problem):
      # prob_file = StudentProblemFile.get_or_create(required_problem_filename=psfile.)
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
    
    #create the student solution
    # student_ps_sol = StudentProblemSet.objects.get_or_create(problem_set=ps, user=request.user, submitted=timezone.now())
    return HttpResponseRedirect("/results/" + ps_id + "/" + p_id + "/")
    
  else:
    raise Http404("Don't do that")

  pass
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
      # required_pf = RequiredProblemFilename(pk=ps_id)
      # prob_file = StudentProblemFile.get_or_create(required_problem_filename=psfile.)
    
    #getting all the grader files
    for problem in ps.problems.all():
      #create the student problem solution & files
      for psfile in ProblemSolutionFile.objects.filter(problem=problem):
        # prob_file = StudentProblemFile.get_or_create(required_problem_filename=psfile.)
        name = psfile.file_upload.name.split("/")[-1]
        if "makefile" in name.lower():#if makefile is in the name, designate it as THE makefile
          files.append({"localFile" : name, "destFile": "Makefile"})
        else:
          files.append({"localFile" : name, "destFile": name})

    #making Tango run the files
    jobname = slugify(ps.title) + "-" + request.user.username
    body = json.dumps({"image": "autograding_image", "files": files, "jobName": jobname, "output_file": jobname,"timeout": 10})
    #raise Http404(body)
    url = vrfy.settings.TANGO_ADDRESS + "addJob/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title) + "/"
    r = requests.post(url, data=body)
    
    #create the student solution
    # student_ps_sol = StudentProblemSet.objects.get_or_create(problem_set=ps, user=request.user, submitted=timezone.now())
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
  try:
    log_data = json.loads(r.text.split("\n")[-2])#theres a line with an empty string after the last actual output line
  except ValueError: #if the json isn't there, something went wrong when running the job, or the grader file messed up
    raise Http404("Something went wrong. Make sure your code is bug free and resubmit. \nIf the problem persists, contact your professor or TA")
  
  #only send the data that the student should see
  context = {"score_sum" : log_data["score_sum"], "score_key" : log_data["score_key"], "external_log" : log_data["external_log"]}
  return render(request, 'course/results_detail.html', context)
  # return HttpResponse("And Here are the results for one your problem sets")

  #returns the results of a given problem set (and all attempts)
def results_problem_detail(request, p_id, ps_id):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
  problem = get_object_or_404(Problem, pk=ps_id)
  
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
