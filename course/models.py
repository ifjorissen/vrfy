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

class Problem(models.Model):
	# title default could be problem id
	title = models.CharField(max_length=200)
	course = models.CharField(max_length=200)
	statement = models.TextField() #markdown 
	many_attempts = BooleanField(default = True)
	# files_to_upload = 
	# problem descriptions e.g your solution to 
	# list of .py uploads that should be uploaded and extras
	# assigned = models.BooleanField(default = False)

	def __str__(self): 
		return self.title


class ProblemSolution(models.Model):
	#should problem be a One to One Field?:https://docs.djangoproject.com/en/1.8/topics/db/examples/one_to_one/ and
	# https://docs.djangoproject.com/en/1.8/topics/db/examples/many_to_one/
	problem = models.ForeignKey(Problem)
	solution = models.TextField()

	def __str__(self): 
		return self.id


#this has not been tested at all
#should also use student forms probably: https://docs.djangoproject.com/en/1.8/topics/forms/modelforms/#django.forms.ModelForm
class StudentSolution(models.Model):
	problem = models.ForeignKey(Problem)
	ps = models.ForeignKey(ProblemSet)
	user = models.ForeignKey(CSUser)
	submitted = models.DateTimeField('date submitted')
	# files = models.ManyToManyField()
	#user who uploaded
	#problem number
	#problem set number
	#date time
	#submitted files

	#attempt number



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


#ability for jim to access somethign on the order of /m121/folio/jfix/hw1/p1/v1/files/  and /m121/folio/jfix/hw1/p1/v1/files/
#a csv with output for the latest (or best) attempt on the problem set