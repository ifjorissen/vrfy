from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils import timezone
from django.utils.text import slugify
from .models import *
from generic.views import *
from generic.models import CSUser
import requests
import json

from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response

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
  sps_sol, sps_created = StudentProblemSet.objects.get_or_create(problem_set=ps, user=request.user)

  problem_solution_dict = {}
  for problem in ps.problems.all():
    #try to get the student solution
    student_psol, s_created = StudentProblemSolution.objects.get_or_create(problem=problem, student_problem_set=sps_sol)
    problem_solution_dict[problem] = student_psol

  return render(request, 'course/attempt_problem_set.html', {'problem_set': ps, 'problem_set_dict':problem_solution_dict})

def submit_success(request, ps_id, p_id):
  authenticate(request)
  #make sure the job is in the queue
  return render(request, 'course/submit_success.html')



def problem_set_index(request):
  '''
  authenticate the request, return a dict of the (problem sets : student problem set solutions)
  '''
  authenticate(request)
  ps_sol_dict = {}
  latest_problem_sets = ProblemSet.objects.filter(pub_date__lte=timezone.now()).order_by('due_date')
  for ps in latest_problem_sets:
    try:
      student_ps_sol = StudentProblemSet.objects.get(problem_set=ps, user=request.user)
    except StudentProblemSet.DoesNotExist:
      student_ps_sol = None

    ps_sol_dict[ps] = student_ps_sol
  # student_problemset_solutions = [StudentProblemSet.objects.filter(user=request.user, problem_set__id = ps.id) for ps in latest_problem_sets]
  context = {'ps_dict': ps_sol_dict}
  return render(request, 'course/problem_set_index.html', context)

def problem_submit(request, ps_id, p_id):
  authenticate(request)
  if request.method == 'POST':#make sure the user doesn't type this into the address bar
    ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
    problem = get_object_or_404(Problem, pk=p_id)

    #create / get the student problem set and update the submission time (reflects latest attempt)
    student_ps_sol= StudentProblemSet.objects.get(problem_set=ps, user=request.user)
    student_ps_sol.submitted = timezone.now()
    student_ps_sol.save()

    student_psol = StudentProblemSolution.objects.get(problem=problem, student_problem_set=student_ps_sol)
    student_psol.submitted = timezone.now()
    student_psol.attempt_num += 1 
    student_psol.save()
    
    #opens the courselab
    url = vrfy.settings.TANGO_ADDRESS + "upload/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title)+ "_" + slugify(problem.title) + "/"
    files = []

    #getting all the submitted files
    for name, f in request.FILES.items():
      localfile = name + "-"+ request.user.username
      header = {'Filename': localfile}
      r = requests.post(url, data=f.read(), headers=header)
      files.append({"localFile" : localfile, "destFile":name})#for the addJob command
      required_pf = RequiredProblemFilename.objects.get(problem=problem, file_title=name)
      try:
        prob_file = StudentProblemFile.objects.filter(required_problem_filename=required_pf, student_problem_solution = student_psol).latest('attempt_num')
        attempts = prob_file.attempt_num + 1
        new_prob_file = StudentProblemFile.objects.create(required_problem_filename=required_pf, student_problem_solution = student_psol, submitted_file=f, attempt_num = attempts)
        new_prob_file.save()

      except StudentProblemFile.DoesNotExist:
        prob_file = StudentProblemFile.objects.create(required_problem_filename=required_pf, student_problem_solution = student_psol, submitted_file=f)
        prob_file.save()
    
    #add grader libraries
    for lib in GraderLib.objects.all():
      name = lib.lib_upload.name.split("/")[-1]
      files.append({"localFile" : name, "destFile": name})

    #getting all the grader files
    grading = problem.grade_script
    name = grading.name.split("/")[-1]
    files.append({"localFile" : name, "destFile": name})

    #add the makefile
    files.append({"localFile" : "autograde-Makefile", "destFile": "Makefile"})

    for psfile in ProblemSolutionFile.objects.filter(problem=problem):
      name = psfile.file_upload.name.split("/")[-1]
      files.append({"localFile" : name, "destFile": name})

    #making Tango run the files
    jobname = slugify(ps.title) + "_" + slugify(problem.title) + "-" + request.user.username
    body = json.dumps({"image": "autograding_image", "files": files, "jobName": jobname, "output_file": jobname,"timeout": 1000})
    #raise Http404(body)
    url = vrfy.settings.TANGO_ADDRESS + "addJob/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title) + "_" + slugify(problem.title) + "/"
    r = requests.post(url, data=body)
    
    # return redirect('course:attempt_problem_set', ps_id)
    return redirect('course:submit_success', ps_id, p_id)
    
  else:
    raise Http404("Don't do that")

#returns the results of a given problem set (and all attempts)
def results_detail(request, ps_id):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
  student_ps = get_object_or_404(StudentProblemSet, problem_set=ps, user=request.user)
  results_dict = {}
  result_set, created = ProblemResultSet.objects.get_or_create(sp_set = student_ps, user=request.user, problem_set=ps)

  for solution in student_ps.studentproblemsolution_set.all():
    if solution.submitted:
      result_obj = ProblemResult.objects.create(sp_sol = solution, result_set=result_set, user=request.user, problem=solution.problem)
  #poll the tango server
      url = vrfy.settings.TANGO_ADDRESS + "poll/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title) + "_" + \
          slugify(solution.problem.title) + "/" + slugify(ps.title) + "_" + \
          slugify(solution.problem.title) + "-" + request.user.username + "/"
      r = requests.get(url)
      try:
        log_data = json.loads(r.text.split("\n")[-2])#theres a line with an empty string after the last actual output line
        #create the result object
        # result_obj.score = log_data["score_sum"]
        result_obj.score = 10
        result_obj.internal_log = log_data["internal_log"]
        result_obj.sanity_log = log_data["sanity_compare"]
        result_obj.external_log = log_data["external_log"]
        result_obj.raw_log = json.dumps(log_data, indent=4)
        result_obj.timezone = timezone.now()
        result_obj.save()
      except ValueError: #if the json isn't there, something went wrong when running the job, or the grader file messed up
        raise Http404("Something went wrong. Make sure your code is bug free and resubmit. \nIf the problem persists, contact your professor or TA")
    
    else:
      result_obj = None
    results_dict[solution] = result_obj
    #make a result object
    #only send the data that the student should see
    context = {'sps': student_ps, "ps_results" : results_dict}
  return render(request, 'course/results_detail.html', context)

def results_problem_detail(request, ps_id, p_id):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
  student_ps = get_object_or_404(StudentProblemSet, problem_set=ps, user=request.user)
  results_dict = {}
  result_set, created = ProblemResultSet.objects.get_or_create(sp_set = student_ps, user=request.user, problem_set=ps)

  for solution in student_ps.studentproblemsolution_set.all():
    if solution.submitted:
      result_obj = ProblemResult.objects.create(sp_sol = solution, result_set=result_set, user=request.user, problem=solution.problem)
  #poll the tango server
      url = vrfy.settings.TANGO_ADDRESS + "poll/" + vrfy.settings.TANGO_KEY + "/" + slugify(ps.title) + "_" + \
          slugify(solution.problem.title) + "/" + slugify(ps.title) + "_" + \
          slugify(solution.problem.title) + "-" + request.user.username + "/"
      r = requests.get(url)
      try:
        log_data = json.loads(r.text.split("\n")[-2])#theres a line with an empty string after the last actual output line
        #create the result object
        # result_obj.score = log_data["score_sum"]
        result_obj.score = 10
        result_obj.internal_log = log_data["internal_log"]
        result_obj.sanity_log = log_data["sanity_compare"]
        result_obj.external_log = log_data["external_log"]
        result_obj.raw_log = json.dumps(log_data, indent=4)
        result_obj.timezone = timezone.now()
        result_obj.save()
      except ValueError: #if the json isn't there, something went wrong when running the job, or the grader file messed up
        raise Http404("Something went wrong. Make sure your code is bug free and resubmit. \nIf the problem persists, contact your professor or TA")
    
    else:
      result_obj = None
    results_dict[solution] = result_obj
    #make a result object
    #only send the data that the student should see
    context = {'sps': student_ps, "ps_results" : results_dict}
  return render(request, 'course/results_detail.html', context)

# def results_index(request):
#   authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  # response = "here are all the results that are availiable"
  #get all the student problem sets
  # sps_sets = StudentProblemSet.objects.filter(user=request.user).order_by('submitted')
  # sps_results_dict = {}
  # for sps in sps_sets:
  #   try:
  #     result_set = ProblemResultSet.objects.get(sp_set=sps)
  #   except ProblemResultSet.DoesNotExist:
  #     result_set = None
  #   sps_results_dict[sps] = result_set
  #show the latest results
  #get the latest result for each existing solution
  # for sps in studentp_sets:
    # results = ProblemResult.objects.filter(user=request.user).order_by('timestamp')
    # context = {'results': results}
  # context = {'sps_results_dict': sps_results_dict}
  # return render(request, 'course/results_index.html', context)
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
