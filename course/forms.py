from django import forms

# imports for modelform
from django.forms import ModelForm
from .models import StudentProblemSolution, StudentProblemSet

# modelform
# 
class StudentProblemSolutionForm(ModelForm):
    #applicant info
    class Meta:
      model = StudentProblemSolution
      exclude = ('job_id', 'task_id')