from django.db import models
from django.contrib.auth.models import User
from vrfy.settings import TEST
import ldap3
from ldap3 import ASYNC, SYNC, ALL_ATTRIBUTES, Server, Connection, SUBTREE, ALL

# from generic.models import CSUser

# Create your models here.
class Reedie(models.Model):
  user = models.OneToOneField(User)
  role = models.CharField(max_length=40)
  last_updated = models.DateTimeField('most recent ldap query', null=True)

  def __str__(self):
    return self.user.username

  def first_name(self):
    return self.user.first_name

  def last_name(self):
    return self.user.last_name

  def email(self):
    return self.user.email

# class Enrollment(models.Model):
#   student = models.ForeignKey(Reedie, on_delete=models.CASCADE)
#   section = models.ForeignKey('Section', related_name='enrolled', on_delete=models.CASCADE)
#   date_joined = models.DateField('date added to section')

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
  # enrolled = models.ManyToManyField(Reedie, through='Enrollment')
  enrolled = models.ManyToManyField(Reedie, related_name='enrolled')
  # enrolled = models.ManyToManyField('generic.CSUser', related_name='enrolled', blank=True)
  # prof = models.ForeignKey('generic.CSUser', null=True, blank=True)
  prof = models.ForeignKey(User, null=True, blank=True)
  #one more model to TAs?

  def __str__(self):
    return self.course.title + ": " + self.section_id
