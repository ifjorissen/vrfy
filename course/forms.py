from django import forms

# imports for modelform
from django.forms import ModelForm
from .models import StudentProblemSolution

# class SOSGrantAppForm(forms.Form):
#     #applicant info
#     name = forms.CharField(label='Your name', max_length=100)
#     preferred_pron = forms.CharField(max_length = 30, blank=True)
#     major = forms.CharField(max_length = 30)
#     # year = forms.IntegerField(max_length = 1, choices = YEARS)

#     #contact info
#     address = forms.CharField(max_length = 50)
#     phone = forms.CharField(max_length = 15)
#     email = forms.EmailField()

    #questions

    # contact = forms.ForeignKey(SinUser, null=True)
    # description = forms.TextField()

# modelform
# 
class StudentProblemSolutionForm(ModelForm):
    #applicant info
    class Meta:
      model = StudentProblemSolution
      exclude = ('job_id', 'task_id')