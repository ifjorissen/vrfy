from django import forms
from .models import Problem, ProblemSet, StudentSolution


# class FileUploadForm(forms.Form):
#   title = forms.CharField() #file name to upload

class StudentSolutionForm(forms.Form):
  your_name = forms.CharField(label='Your name', max_length=100)
