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

  def __str__(self):
    return self.user.username

  def first_name(self):
    return self.user.first_name

  def last_name(self):
    return self.user.last_name

  def email(self):
    return self.user.email
  
  def ldap_lookup_user(self, username):
    # print("lookup called with {!s}".format(username))
    #to do: make this asynchronous
    server = Server('ldap.reed.edu', port=389, get_info=ALL)
    con = Connection(server, auto_bind=True)
    query = 'uid={!s},ou=people,dc=reed,dc=edu'.format(username)
    con.search(search_base = query, search_filter = '(objectClass=*)', search_scope = SUBTREE, attributes=ALL_ATTRIBUTES)

    if TEST:
      result = {
        "cn": [
          "Isabella F Jorissen",
          "ijorissen"
        ],
        "eduPersonAffiliation": [
          "student"
        ],
        "eduPersonEntitlement": [
          "cascade",
          "thesis-vpn"
        ],
        "eduPersonPrimaryAffiliation": "student",
        "eduPersonPrincipalName": "isjoriss@REED.EDU",
        "gecos": "Isabella F Jorissen",
        "gidNumber": 503,
        "givenName": [
          "Isabella"
        ],
        "homeDirectory": "/afs/reed.edu/user/i/s/isjoriss",
        "loginShell": "/bin/bash",
        "mail": [
          "isjoriss@reed.edu"
        ],
        "objectClass": [
          "top",
          "inetOrgPerson",
          "eduPerson",
          "ReedCollegePerson",
          "posixAccount",
          "inetLocalMailRecipient"
        ],
        "rcLocalHomeDirectory": "/home/isjoriss",
        "rcMiddleName": [
          "F"
        ],
        "sn": [
          "Jorissen"
        ],
        "uid": [
          "isjoriss"
        ],
        "uidNumber": 39878}
    else:
      result = con.response[0]['attributes']
    return result

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
  enrolled = models.ManyToManyField(Reedie, related_name='enrolled', blank=True)
  # enrolled = models.ManyToManyField(User, related_name='enrolled', blank=True)
  # enrolled = models.ManyToManyField('generic.CSUser', related_name='enrolled', blank=True)
  # prof = models.ForeignKey('generic.CSUser', null=True, blank=True)
  prof = models.ForeignKey(User, null=True, blank=True)
  #one more model to TAs?

  def __str__(self):
    return self.course.title + ": " + self.section_id
