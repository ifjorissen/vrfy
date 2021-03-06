from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponsePermanentRedirect
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.text import slugify
from .models import *
from django.contrib.auth.decorators import login_required
import requests
import json
import time
import datetime
from itertools import chain
from util import tango
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt


#paginator for problem_set_index and your_solutions
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys
sys.path.append("../")
import vrfy.settings

#import celery tasks
from .tasks import *

#import django.contrib.staticfile.views.serve 
#so we can make a view to allow admins to see problem assets
from django.contrib.staticfiles import views

# from celery import group, chord, chain

# the name the form field gives to additional files
ADDITIONAL_FILE_NAME = "additional"
MAX_ADDITIONAL_FILES = 7 

# these helper functions enforce the universal restrictions on what
# problemsets a user can get


def _get_problem_set(pk, reedie):  # if you want one problem set
    return get_object_or_404(
        ProblemSet,
        pk=pk,
        pub_date__lte=timezone.now(),
        cs_section__in=reedie.enrolled.all())


def _query_problem_sets(reedie):  # if you want a queryset
    return ProblemSet.objects.filter(
        pub_date__lte=timezone.now(),
        cs_section__in=reedie.enrolled.all())

def _get_problem_result(solution, request):
    '''
    attempt to get the problem from tango if it's been autograded
    if not, get the normal result
    if the result doesn't exist, return none
    '''
    ps = solution.student_problem_set.problem_set
    # poll the tango server
    if solution.problem.autograde_problem:
        prob_result = ProblemResult.objects.get(
            sp_sol=solution,
            job_id=solution.job_id,
            attempt_num=solution.attempt_num)
    else:
        # special not-autograded stuff goes here
        prob_result = ProblemResult.objects.get(
            sp_sol=solution, attempt_num=solution.attempt_num)

    return prob_result


@login_required
def index(request):
    # problems due in the next week
    ps_set = _query_problem_sets(
        request.user.reedie).filter(
        due_date__range=(
            timezone.now(),
            (timezone.now() +
             datetime.timedelta(
                days=7)))).order_by('due_date')
    # ps_set = []
    ps_rs_dict = {}
    for ps in ps_set:
        try:
            sp_set = StudentProblemSet.objects.get(
                problem_set=ps, user=request.user.reedie)
            ps_rs_dict[ps] = sp_set
        except StudentProblemSet.DoesNotExist:
            ps_rs_dict[ps] = None

    # student problems submitted in the last 24hrs
    recent_solutions = StudentProblemSolution.objects.filter(
        student_problem_set__user=request.user.reedie,
        submitted__gte=(
            timezone.now() -
            datetime.timedelta(
                days=1)))
    context = {'upcoming_sets_results_dict': ps_rs_dict,
               'recently_submitted_solutions': recent_solutions}
    return render(request, 'course/index.html', context)


@login_required
def logout_user(request):
    logout(request)
    # return
    # HttpResponseRedirect('https://weblogin.reed.edu/cgi-bin/logout?https://cs.reed.edu/logged_out/')
    forward_url = request.GET.get(
        'forward_url',
        'https://weblogin.reed.edu/cgi-bin/logout?https://cs.reed.edu/logged_out/')
    response = HttpResponsePermanentRedirect(forward_url)
    response.delete_cookie(key='cosign-cs')
    return response


def logout_view(request):
    logout(request)
    context = {}
    return render(request, 'course/logged_out.html', context)

@login_required
def your_solutions(request):
    """
    Display all of the solutions a student has submitted

    **Context**

    ``solutions``
        the solutions for request.user's problems of type :model:`course.StudentProblemSolution`.

    **Template:**

    :template:`templates/course/your_solutions.html`

    """
    all_solutions = StudentProblemSolution.objects.filter(
        student_problem_set__user=request.user.reedie).order_by('-submitted')

    paginator = Paginator(all_solutions, 8)
    page = request.GET.get('page')

    try:
        solutions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        solutions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        solutions = paginator.page(paginator.num_pages)

    context = {'solutions': solutions}
    return render(request, 'course/your_solutions.html', context)



@login_required
def attempt_problem_set(request, ps_id):
    '''
    when a student attempts a problem set, try to get their solution set & solutions if they exist
    '''
    if request.method == 'GET':
        ps = _get_problem_set(ps_id, request.user.reedie)
        problem_solution_dict = {}
        try:
            sp_set = StudentProblemSet.objects.get(
                problem_set=ps, user=request.user.reedie)
            for problem in ps.problems.all():
                try:
                    student_psol = StudentProblemSolution.objects.get(
                        problem=problem, student_problem_set=sp_set)
                except StudentProblemSolution.DoesNotExist:
                    student_psol = None
                problem_solution_dict[problem] = student_psol
        except StudentProblemSet.DoesNotExist:
            problem_solution_dict = {
                problem: None for problem in ps.problems.all()}
        context = {
            'problem_set': ps,
            'problem_solution_dict': problem_solution_dict,
            'additional_file_name': ADDITIONAL_FILE_NAME,
            'max_additional_files': MAX_ADDITIONAL_FILES}
        return render(request, 'course/attempt_problem_set.html', context)
    else:
        raise Http404("Don't do that")


@login_required
def submit_success(request, ps_id, p_id):
    ps = _get_problem_set(ps_id, request.user.reedie)
    problem = get_object_or_404(Problem, pk=p_id)

    if problem.autograde_problem:  # if it is running in Tango
        # get running jobs
        job_url = vrfy.settings.TANGO_ADDRESS + \
            "jobs/" + vrfy.settings.TANGO_KEY + "/0/"
        running_jobs = requests.get(job_url)
        rj_json = running_jobs.json()

        jobName = tango.get_jobName(problem, ps, request.user.username)
        job_running = False
        for job in rj_json["jobs"]:
            if job["name"] == jobName:
                job_running = True

        context = {
            "num_jobs": len(
                rj_json["jobs"]),
            "job_running": job_running,
            'ps_id': ps_id,
            'p_id': p_id}
        # make sure the job is in the queue
        return render(request, 'course/submit_success.html', context)

    else:  # if it's a human graded problem
        return results_problem_detail(request, ps_id, p_id)

#IFJ: 1.24.16-- There is probably a better & more secure way to do this
@csrf_exempt
def notifyURL(request, spsol_id, probres_id):
    if request.method == 'POST':
        f = request.FILES['file']
        tango_result = f.read()
        tango_result = tango_result.decode(('utf-8'))

        task = save_autograde_results.delay(spsol_id, probres_id, tango_result)        
        response = HttpResponse()
        response.status_code = 202
        return response
    else:
        return HttpResponseForbidden("Don't do that.") 


@login_required
def serve_problem_asset(request, path):
    '''
    a wrapper function around django.contrib.staticfiles.views.serve()
    to serve problem assets to superusers only
    '''
    if request.user.is_superuser:
        return views.serve(request, path, show_indexes=True)
    else:
        return HttpResponseForbidden("Don't do that.")

@login_required
def problem_set_index(request):
    '''
    return a dict of the (problem sets : student problem set solutions)
    '''
    ps_sol_dict = {}
    problem_sets = _query_problem_sets(
        request.user.reedie).order_by('due_date')

    paginator = Paginator(problem_sets, 8)
    page = request.GET.get('page')

    try:
        latest_problem_sets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        latest_problem_sets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        latest_problem_sets = paginator.page(paginator.num_pages)

    for ps in latest_problem_sets:
        try:
            student_ps_sol = StudentProblemSet.objects.get(
                problem_set=ps, user=request.user.reedie)
        except StudentProblemSet.DoesNotExist:
            student_ps_sol = None

        ps_sol_dict[ps] = student_ps_sol

    # student_problemset_solutions = [StudentProblemSet.objects.filter(user=request.user, problem_set__id = ps.id) for ps in latest_problem_sets]
    context = {'ps_dict': ps_sol_dict, 'ps_sets':latest_problem_sets}
    return render(request, 'course/problem_set_index.html', context)


@login_required
def problem_submit(request, ps_id, p_id):
    if request.method == 'POST':  # make sure the user doesn't type this into the address bar
        ps = _get_problem_set(ps_id, request.user.reedie)
        problem = get_object_or_404(Problem, pk=p_id)

        # create / get the student problem set and update the submission time
        # (reflects latest attempt)
        student_ps_sol, sp_set_created = StudentProblemSet.objects.get_or_create(
            problem_set=ps, user=request.user.reedie, defaults={'submitted': timezone.now()})
        student_ps_sol.save()

        student_psol, sp_sol_created = StudentProblemSolution.objects.get_or_create(
            problem=problem, student_problem_set=student_ps_sol)
        student_psol.submitted = timezone.now()
        prevscore = student_psol.latest_score()
        student_psol.attempt_num += 1
        student_psol.save()

        # create the student result set & problem
        # result_set, prs_created = ProblemResultSet.objects.get_or_create(sp_set = student_ps_sol, user=request.user, problem_set=ps)
        mytimestamp = None
        if not problem.autograde_problem:  # if its not being autograded, we should set the timestamp here; if it is, tango will set it
            mytimestamp = timezone.now()
        prob_result = ProblemResult.objects.create(
            attempt_num=student_psol.attempt_num,
            sp_sol=student_psol,
            sp_set=student_ps_sol,
            user=request.user.reedie,
            problem=problem,
            timestamp=mytimestamp)

        additional_files = 0
        files = []  # for the addJob
        file_batch = [] #for the celery tasks
        # getting all the submitted files
        for name, f in request.FILES.items():
            # print(name, ADDITIONAL_FILE_NAME)
            if ADDITIONAL_FILE_NAME in name:
                required_pf = None
                # print(additional_files)
                if additional_files < MAX_ADDITIONAL_FILES:
                    additional_files += 1
                else:
                    return render(request, '403.html', {'exception': "You can't upload more than " + str(
                        MAX_ADDITIONAL_FILES) + " additional files."}, status=403)
                    #raise PermissionDenied()

            else:
                required_pf = RequiredProblemFilename.objects.get(
                    problem=problem, file_title=name)

            if required_pf is None or not required_pf.force_rename:
                name = f.name  # if the file should not be renamed, give it the name as it was uploaded

                # we also need to check if it has the same name as any of the
                # grader files
                for gfile in chain(problem.problemsolutionfile_set.all(), GraderLib.objects.all(), [
                                   problem.grade_script.name.split("/")[-1]]):
                    if name == str(gfile):
                        return render(
                            request, '403.html', {
                                'exception': name + " is an invalid filename."}, status=403)
                        #raise PermissionDenied(name + " is an invalid filename.")

            if problem.autograde_problem:
                localfile = name + "-" + request.user.username
                file_batch.append(send_file_to_tango.s(ps_id, p_id, request.user.reedie.id, localfile, f.read()))
                # for the addJob command
                files.append({"localFile": localfile, "destFile": name})

            #IFJ 1.20.16: this can be a celery task
            attempts = student_psol.attempt_num
            new_prob_file = StudentProblemFile.objects.create(
                required_problem_filename=required_pf,
                student_problem_solution=student_psol,
                submitted_file=f,
                attempt_num=attempts)
            new_prob_file.save()

        if problem.autograde_problem:  # these operatons are only required for autograding
            #IFJ 1.20.16 TODO: edit this so only this course's grader libs get uploaded
            # add grader libraries
            for lib in GraderLib.objects.all():
                name = lib.lib_upload.name.split("/")[-1]
                files.append({"localFile": name, "destFile": name})

            # getting all the grader files
            grading = problem.grade_script
            name = grading.name.split("/")[-1]
            files.append({"localFile": name, "destFile": name})

            for psfile in ProblemSolutionFile.objects.filter(problem=problem):
                name = psfile.file_upload.name.split("/")[-1]
                files.append({"localFile": name, "destFile": name})

            # upload the json data object
            tango_data = json.dumps(
                {
                    "attempts": student_psol.attempt_num,
                    "prevscore": prevscore,
                    "timedelta": student_psol.is_late()})
            data_name = "data.json" + "-" + request.user.username
            file_batch.append(send_file_to_tango.s(ps_id, p_id, request.user.reedie.id, data_name, tango_data))
            files.append({"localFile": data_name, "destFile": "data.json"})

            #batch upload the files
            jobName = tango.get_jobName(problem, ps, request.user.username)
            file_upload_job = group(file_batch)
            celery_callback = submit_job_to_tango.s(student_psol.id, prob_result.id, files, jobName, problem.time_limit) | get_response.s(prob_result.id)
            add_job_to_tango = (file_upload_job | celery_callback).delay()
        return redirect('course:submit_success', ps_id, p_id)

    else:
        return HttpResponseForbidden("Don't do that")


@login_required
def results_detail(request, ps_id):
    # returns the results of a given problem set (and all attempts)
    # logic to figure out if the results are availiable and if so, get them
    ps = _get_problem_set(ps_id, request.user.reedie)
    sp_set = get_object_or_404(
        StudentProblemSet,
        problem_set=ps,
        user=request.user.reedie)
    # result_set = get_object_or_404(ProblemResultSet, user=request.user, sp_set=student_ps, problem_set=ps)
    results_dict = {}

    # for solution in student_ps.studentproblemsolution_set.all():
    #   results_dict[solution] = _get_problem_result(solution, request)
    for problem in ps.problems.all():
        try:
            sp_sol = StudentProblemSolution.objects.get(
                student_problem_set=sp_set, problem=problem)
            results_dict[problem] = _get_problem_result(sp_sol, request)
        except StudentProblemSolution.DoesNotExist:
            results_dict[problem] = None
        except ValueError:  # there was a problem reading the json_log
            context = {
                'exception': "Something went wrong. Our autograder is likely encountering a runtime error. Did you run (and test) your code? If not, make sure your code is bug free and resubmit. \nIf the problem persists, contact your professor or TA, as it might be a problem with the grading script."}
            return render(request, '500.html', context, status=500)

    # make a result object
    # only send the data that the student should see
    context = {'sps': sp_set, "ps_results": results_dict}
    return render(request, 'course/results_detail.html', context)


@login_required
def results_problem_detail(request, ps_id, p_id):
    # logic to figure out if the results are availiable and if so, get them
    ps = _get_problem_set(ps_id, request.user.reedie)
    problem = get_object_or_404(Problem, pk=p_id)
    sp_set = get_object_or_404(
        StudentProblemSet,
        problem_set=ps,
        user=request.user.reedie)
    results_dict = {}
    # result_set, created = ProblemResultSet.objects.get_or_create(sp_set = student_ps, user=request.user, problem_set=ps)
    sp_sol = get_object_or_404(
        StudentProblemSolution,
        student_problem_set=sp_set,
        problem=problem)

    try:
        result = _get_problem_result(sp_sol, request)
    except ValueError:  # if there was a problem reading the json
        context = {
            'exception': "Something went wrong. Our autograder is likely encountering a runtime error. Did you run (and test) your code?  If not, make sure your code is bug free and resubmit. \nIf the problem persists, contact your professor or TA, as it might be a problem with the grading script."}
        return render(request, '500.html', context, status=500)

    context = {'solution': sp_sol, "result": result}
    return render(request, 'course/results_problem_detail.html', context)
