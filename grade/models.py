from django.db import models
from django.core.urlresolvers import reverse
from django.forms import ModelForm

#A single assignment for the student. Tango defines these as "courselabs"
class Assignment(models.Model):
    public_name = models.CharField(max_length=200)#name as it will appear on the website
    tango_name = models.CharField(max_length=200, editable=False)#name as tango will know it
    available = models.BooleanField() #whether or not students can see this assignment

    def get_absolute_url(self):
        return reverse('assignment-detail', kwargs={'pk': self.pk})

#File that has been sent to the tango server under a specific assignment
class File(models.Model):
    #the addjob command in tango requires a name for the file as it was submitted(localname) and as it will be run(destname)
    local_name = models.CharField(max_length=200, editable=False) 
    dest_name = models.CharField(max_length=200)#one of the destnames needs to be 'Makefile' otherwise nothing will run
    assignment = models.ForeignKey(Assignment)

class AssignmentForm(ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'
