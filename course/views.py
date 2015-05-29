from django.shortcuts import render
from django.http import HttpResponse, Http404 
from .models import ProblemSet
from generic.views import *
from generic.models import CSUser

def index(request):
  authenticate(request)
  latest_problem_sets = ProblemSet.objects.order_by('-pub_date')[:5]
  context = {'latest_problem_sets': latest_problem_sets}
  return render(request, 'course/index.html', context)

def problem_set(request, ps_id):
  authenticate(request)
  try:
    ps = ProblemSet.objects.get(pk=ps_id)
  except ProblemSet.DoesNot.Exist:
      raise Http404("Problem Set Does Not Exist (or has yet to be released)")

  response = "here's that problem set: {!s} you clicked on".format(ps_id)
  return render(request, 'course/problem_set_detail.html', {'problem_set': ps})

def results(request):
  authenticate(request)
  return HttpResponse("And Here are the results for one your problem sets")