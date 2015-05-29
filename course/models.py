from django.db import models

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
	statement = models.TextField()
	# assigned = models.BooleanField(default = False)

	def __str__(self): 
		return self.title


class ProblemSolution(models.Model):
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