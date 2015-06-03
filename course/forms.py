from django import forms
from .models import Problem, ProblemSet, StudentSolution


# class FileUploadForm(forms.Form):
# 	title = forms.CharField() #file name to upload
	



class StudentSolutionForm(forms.ModelForm):
	class Meta:
		model = StudentSolution