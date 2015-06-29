from django import forms
from django.forms.models import modelformset_factory
from .models import Problem, ProblemSet, StudentSolution


# class FileUploadForm(forms.Form):
#   title = forms.CharField() #file name to upload

#class StudentSolutionForm(forms.Form):
#  your_name = forms.CharField(label='Your name', max_length=100)

# 	title = forms.CharField() #file name to upload
	
#https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/#model-formsets
StudentProblemFileFormSet = modelformset_factory(StudentProblemFile, fields=('submitted_file'))

# class StudentProblemFileForm(forms.ModelForm):
# 	class Meta: 
# 		model = StudentProblemFile
# 		fields = ['submitted_file']

# class StudentSolutionForm(forms.ModelForm):
# 	class Meta:
# 		model = StudentSolution

