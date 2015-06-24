from django.db import models

#A single assignment for the student. Tango defines these as "courselabs"
class Assignment(models.Model):
    name = models.CharField(max_length=200)
    available = models.BooleanField() #whether or not students can see this assignment

#File that has been sent to the tango server under a specific assignment
class File(models.Model):
    #the addjob command in tango requires a name for the file as it was submitted(localname) and as it will be run(destname)
    localname = models.CharField(max_length=200, editable=False) 
    destname = models.CharField(max_length=200)#one of the destnames needs to be 'Makefile' otherwise nothing will run
    assignment = models.ForeignKey(Assignment)
