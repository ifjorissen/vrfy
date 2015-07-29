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
import ast
import time
from util import tango

from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response

import sys
sys.path.append("../")
import vrfy.settings

ADDITIONAL_FILE_NAME = "additional"

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
  
  problem = get_object_or_404(Problem, pk=p_id)

  if problem.autograde_problem:#if it is running in Tango
    job_url = vrfy.settings.TANGO_ADDRESS + "jobs/" + vrfy.settings.TANGO_KEY + "/0/"
    dead_job_url = vrfy.settings.TANGO_ADDRESS + "jobs/" + vrfy.settings.TANGO_KEY + "/1/"
    info_url = vrfy.settings.TANGO_ADDRESS + "info/" + vrfy.settings.TANGO_KEY +"/"

    running_jobs = requests.get(job_url)
    dead_jobs = requests.get(dead_job_url)
    info = requests.get(info_url)

    dj_json = dead_jobs.json()
    rj_json = running_jobs.json()
    info_json = info.json()
    context = {"info":info_json["info"], "jobs":rj_json, "dead_jobs":dj_json}
    #make sure the job is in the queue
    return render(request, 'course/submit_success.html', context)

  else:#if it's a human graded problem
    return redirect('course:problem_set_index')

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

    #create the student result set & problem
    result_set, prs_created = ProblemResultSet.objects.get_or_create(sp_set = student_ps_sol, user=request.user, problem_set=ps)
    mytimestamp = None
    if not problem.autograde_problem: #if its not being autograded, we should set the timestamp here; if it is, tango will set it
      mytimestamp = timezone.now()
    prob_result = ProblemResult.objects.create(sp_sol=student_psol, result_set=result_set, user=request.user, problem=problem, timestamp=mytimestamp)
    
    files = []#for the addJob
    #getting all the submitted files
    for name, f in request.FILES.items():

      if name == ADDITIONAL_FILE_NAME:
        required_pf = None
      else:
        required_pf = RequiredProblemFilename.objects.get(problem=problem, file_title=name)

      if required_pf == None or not required_pf.force_rename: 
        name = f.name#if the file should not be renamed, give it the name as it was uploaded
        #we also need to check if it has the same name as any of the grader files
        for psfile in problem.problemsolutionfile_set.all():
          if name == psfile.file_upload.name.split("/")[-1]:
            raise Http404("HEY! You can't name your file " + name + ". Because.... reasons.")
        
        if name == problem.grade_script.name.split("/")[-1]:
          raise Http404("HEY! You can't name your file " + name + ". Because.... reasons.")
        
        for lib in GraderLib.objects.all():
          if name == lib.lib_upload.name.split("/")[-1]:
            raise Http404("HEY! You can't name your file " + name + ". Because.... reasons.")
        
      localfile = name + "-"+ request.user.username
      if problem.autograde_problem:
        r = tango.upload(problem, ps, localfile, f.read())
        files.append({"localFile" : localfile, "destFile":name})#for the addJob command
      
      try:
        prob_file = StudentProblemFile.objects.filter(required_problem_filename=required_pf, student_problem_solution = student_psol).latest('attempt_num')
        attempts = prob_file.attempt_num + 1
        new_prob_file = StudentProblemFile.objects.create(required_problem_filename=required_pf, student_problem_solution = student_psol, submitted_file=f, attempt_num = attempts)
        new_prob_file.save()

      except StudentProblemFile.DoesNotExist:
        prob_file = StudentProblemFile.objects.create(required_problem_filename=required_pf, student_problem_solution = student_psol, submitted_file=f)
        prob_file.save()

    if problem.autograde_problem:#these operatons are only required for autograding

      #add grader libraries
      for lib in GraderLib.objects.all():
        name = lib.lib_upload.name.split("/")[-1]
        files.append({"localFile" : name, "destFile": name})

      #getting all the grader files
      grading = problem.grade_script
      name = grading.name.split("/")[-1]
      files.append({"localFile" : name, "destFile": name})

      for psfile in ProblemSolutionFile.objects.filter(problem=problem):
        name = psfile.file_upload.name.split("/")[-1]
        files.append({"localFile" : name, "destFile": name})

      #upload the json data object
      tango_data = json.dumps({"attempts": student_psol.attempt_num, "timedelta": student_psol.is_late()})
      data_name = "data.json" + "-" + request.user.username
      tango.upload(problem, ps, data_name, tango_data)
      files.append({"localFile" : data_name, "destFile": "data.json"})

      #making Tango run the files
      jobName = slugify(ps.title) + "_" + slugify(problem.title) + "-" + request.user.username
      r = tango.addJob(problem, ps, files, jobName, jobName)

      if r.status_code is not 200:
        return redirect('500.html')
      else:
        response = r.json()
        student_psol.job_id = response["jobId"]
        prob_result.job_id = response["jobId"]
        student_psol.save()
        prob_result.save()
    return redirect('course:submit_success', ps_id, p_id)
    
  else:
    raise Http404("Don't do that")

#returns the results of a given problem set (and all attempts)
def results_detail(request, ps_id):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  ps = get_object_or_404(ProblemSet, pk=ps_id, pub_date__lte=timezone.now())
  student_ps = get_object_or_404(StudentProblemSet, problem_set=ps, user=request.user)
  result_set = get_object_or_404(ProblemResultSet, user=request.user, sp_set=student_ps, problem_set=ps)
  results_dict = {}

  for solution in student_ps.studentproblemsolution_set.all():
    if solution.submitted:
      prob_result = ProblemResult.objects.filter(sp_sol = solution, job_id=solution.job_id).latest('timestamp')
      
      #poll the tango server
      if solution.problem.autograde_problem:
        outputFile = slugify(ps.title) + "_" +slugify(solution.problem.title) + "-" + request.user.username
        r = tango.poll(solution.problem, ps, outputFile)
        line = r.text.split("\n")[-2]#theres a line with an empty string after the last actual output line
        tango_time = r.text.split("\n")[0].split("[")[1].split("]")[0] #the time is on the first line surrounded by brackets
        tango_time = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(tango_time, '%a %b %d %H:%M:%S %Y'))
        print(tango_time)
        print(prob_result.timestamp)
        
        if tango_time != str(prob_result.timestamp).split("+")[0]:
          if "Autodriver: Job timed out after " in line: #thats the text that Tango outputs when a job times out
            prob_result.score = 0
            prob_result.external_log = ["Program timed out after " + line.split(" ")[-2] + " seconds."]
            prob_result.timestamp = timezone.now()
            prob_result.save()
          else:
            try:
              log_data = json.loads(line)
              #create the result object
              prob_result.score = log_data["score_sum"]
              prob_result.internal_log = log_data["internal_log"]
              prob_result.sanity_log = log_data["sanity_compare"]
              prob_result.external_log = log_data["external_log"]
              prob_result.raw_log = log_data
              prob_result.timestamp = tango_time
              prob_result.save()
            except ValueError: #if the json isn't there, something went wrong when running the job, or the grader file messed up
              raise Http404("Something went wrong. Make sure your code is bug free and resubmit. \nIf the problem persists, contact your professor or TA")
      
      else:
        #special not-autograded stuff goes here
        pass

    else:
      prob_result = None
    results_dict[solution] = prob_result
    
    #if the external log cannot be evaluated as a list, then output it's raw text
    try:
      results_dict[solution].external_log = ast.literal_eval(prob_result.external_log)
    except SyntaxError:#pretty inefficient, but I couldnt find a more elegant solution
      results_dict[solution].external_log = [prob_result.external_log]
    
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
      outputFile = slugify(ps.title) + "_" +slugify(solution.problem.title) + "-" + request.user.username
      r = tango.poll(solution.problem, ps, outputFile)
      try:
        log_data = json.loads(r.text.split("\n")[-2])#theres a line with an empty string after the last actual output line
        #create the result object
        # result_obj.score = log_data["score_sum"]
        result_obj.score = 10
        result_obj.internal_log = log_data["internal_log"]
        result_obj.sanity_log = log_data["sanity_compare"]
        result_obj.external_log = log_data["external_log"]
        result_obj.raw_log = json.dumps(log_data, indent=4)
        result_obj.timestamp = timezone.now()
        result_obj.save()
      except ValueError: #if the json isn't there, something went wrong when running the job, or the grader file messed up
        raise Http404("Something went wrong. Make sure your code is bug free and resubmit. \nIf the problem persists, contact your professor or TA")
    
    else:
      result_obj = None
    results_dict[solution] = result_obj
    #only send the data that the student should see
    context = {'sps': student_ps, "ps_results" : results_dict}
  return render(request, 'course/results_detail.html', context)
