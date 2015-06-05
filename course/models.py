from django.db import models
from generic.models import CSUser


# Create your models here.

# A problem model, which requires:
# a problem title 
# a class associated with the problem
# and a problem description
# To do: potentially make the class a tag instead
# boolean = assigned or not assigned (should remove??)
# problem set it's assoicated with
# each problem points to a set of user submitted solutions
# as well as a summary of results 


#jim should be able to upload a markdown (or html file) for his problem sets and have it display
class Problem(models.Model):
	# title default could be problem id
	title = models.CharField(max_length=200)
	course = models.CharField(max_length=200)
	description = models.TextField(default='') #a short tl;dr of the problem, what to read
	statement = models.TextField(default='') #markdown compatible
	many_attempts = models.BooleanField(default = True)
	# problem_files = models.ManyToManyField('ProblemFile', related_name='required_files')
	# files_to_upload = 
	# problem descriptions e.g your solution to 
	# list of .py uploads that should be uploaded and extras
	# assigned = models.BooleanField(default = False)

	def __str__(self): 
		return self.title

class ProblemFile(models.Model):
	file_title = models.CharField(max_length=200)
	problem = models.ForeignKey(Problem, null=True)

	def __str__(self):
		return self.file_title

	#make sure you validate extension



class ProblemSolution(models.Model):
	#should problem be a One to One Field?:https://docs.djangoproject.com/en/1.8/topics/db/examples/one_to_one/ and
	#https://docs.djangoproject.com/en/1.8/topics/db/examples/many_to_one/
	problem = models.ForeignKey(Problem)
	solution = models.TextField()

	def __str__(self): 
		return self.id


class ProblemSet(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(default='')
	problems = models.ManyToManyField(Problem)
	# submissions = models.IntegerField('number of submissions', default = 0)
	# solutions = models.ManyToManyField(ProblemSolution)
	pub_date = models.DateTimeField('date assigned')
	due_date = models.DateTimeField('date due')

	def __str__(self): 
		return self.title


#this has not been tested at all
#should also use student forms probably: https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/#django.forms.ModelForm
class StudentSolution(models.Model):
	#email field to email users when result is ready
	problem = models.ForeignKey(Problem)
	ps = models.ForeignKey(ProblemSet)
	user = models.ForeignKey(CSUser)
	submitted = models.DateTimeField('date submitted')
	# attempt_num = models.IntegerField(default=1) //shoudl be max of the file uploads
	# submitted_files = models.ManyToManyField(StudentProblemFile)
	# files = models.ManyToManyField()
	#user who uploaded
	#problem number
	#problem set number
	#date time
	#submitted files

	#attempt number

class StudentProblemFile(models.Model):
	prob_file = models.ForeignKey(ProblemFile)
	solution = models.ForeignKey(StudentSolution, null=True)
	# potentially could automatically upload to afs
	submitted_file = models.FileField()
	attempt_num = models.IntegerField(default=1)



#ability for jim to access something on the order of /m121/folio/jfix/hw1/p1/v1/files/  and /m121/folio/jfix/hw1/p1/v1/files/
#a csv with output for the latest (or best) attempt on the problem set