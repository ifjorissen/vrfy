from django.db import models
from generic.models import CSUser

# Create your models here.


class Course(models.Model):
  title = models.CharField(max_length=200)
  num = models.IntegerField()

  def __str__(self):
    return self.title

class Section(models.Model):
  course = models.ForeignKey(Course)
  section_id = models.CharField(max_length=20)
  start_date = models.DateTimeField('course start date')
  end_date = models.DateTimeField('course end date')
  enrolled = models.ManyToManyField('generic.CSUser', related_name='enrolled', blank=True)
  prof = models.ForeignKey('generic.CSUser', null=True, blank=True)
  #one more model to TAs?

  def __str__(self):
    return self.course.title + ": " + self.section_id
