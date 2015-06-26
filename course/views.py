from django.shortcuts import render
from django.http import HttpResponse, Http404 
from .models import ProblemSet
from generic.views import *
from generic.models import CSUser
from django.forms.models import inlineformset_factory

def index(request):
  authenticate(request)
  return render(request, 'course/index.html')


def problem_set_index(request):
  authenticate(request)
  latest_problem_sets = ProblemSet.objects.order_by('-pub_date')[:5]
  context = {'latest_problem_sets': latest_problem_sets}
  return render(request, 'course/problem_set_index.html', context)

def problem_set_detail(request, ps_id):
  authenticate(request)
  try:
    ps = ProblemSet.objects.get(pk=ps_id)
  except ProblemSet.DoesNot.Exist:
      raise Http404("Problem Set Does Not Exist (or has yet to be released)")

  response = "here's that problem set: {!s} you clicked on".format(ps_id)
  return render(request, 'course/problem_set_detail.html', {'problem_set': ps})

#submission & files urls; summary of a problem set & files submitted
#ability to view each attempt and the files submitted with each attempt

#returns the results of a given problem set (and all attempts)
def results_detail(request, ps_id):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  response = "here's the results for that problem set: {!s} you clicked on".format(ps_id)
  return render(request, 'course/results_detail.html', {'problem_set': ps})
  # return HttpResponse("And Here are the results for one your problem sets")

def results_index(request):
  authenticate(request)
  # logic to figure out if the results are availiable and if so, get them
  response = "here are all the results that are availiable"
  return render(request, 'course/results_index.html')
  # return HttpResponse("And Here are the results for your problem sets")

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