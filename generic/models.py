from django.db import models
from django.contrib.auth.models import User
import ldap3
from ldap3 import ASYNC, SYNC, ALL_ATTRIBUTES, Server, Connection, SUBTREE, ALL
from vrfy.settings import TEST, SERVER_EMAIL

# Create your models here.
# Potentially use factors to allow a user to see certain problem sets based on the class they're in

class CSUser(User):
  '''Basic features and properties of a student enrolled in a CS class.

  Attributes:
    attended_signator_trainging(bool): whether the student attended
    signator training. 
    username(str): the username, based on their Reed email
    first_name(str): the users first name
    last_name(str): the users last name
    email(str): the users email
  '''

  @classmethod
  def ldap_lookup_user(cls, username):
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


  @classmethod
  def get_ldap_user(self, username):

    u = CSUser()
    user_dict = CSUser.ldap_lookup_user(username)

    # Getting some data on the user
    u.username = user_dict['uid'][0]
    try:
      u.first_name = user_dict['displayName'][0]
    except KeyError:
      self.first_name = user_dict['givenName'][0]
    u.last_name = user_dict['sn'][0]
    u.email = user_dict['mail'][0]
    # u.factors = 0

    # try: 
    #   # potentially introduces the problem where u has been updated and u != usr but u.username = usr.username
    #   usr = CSUser.objects.get(username=u.username) 
    #   pass
    # except CSUser.DoesNotExist:
    #   usr = u
    #   usr.save()
    usr, created = CSUser.objects.get_or_create(username= u.username)

    # Creating the authenticating factors
    # factor_list = []
    # affiliation = user_dict['eduPersonPrimaryAffiliation'][0]
    # if affiliation in FACTORS:
    #   factor_list.append(affiliation)
    # factor_list.append('student')
    # u.set_factor_list(factor_list)
    # u.save()
   
    return usr
    
  def refresh_from_ldap(self):
    user_dict = CSUser.ldap_lookup_user(self.username)
    # user_dict = results[0][1][1]
    self.username = user_dict['uid'][0]
    try:
      self.first_name = user_dict['displayName'][0]
    except KeyError:
      try:
        self.first_name = user_dict['givenName'][0]
      except KeyError:
        self.first_name = ' '
        self.last_name = user_dict['sn'][0]
        
    # Checks if they have the "mail" attribute, which should filter out
    # alumni
    try:
      self.email = user_dict['mail'][0]
    except:
      pass

    # Creating authenticating factors
    affiliation = user_dict['eduPersonPrimaryAffiliation'][0]
    # factor_list = []
    # if affiliation in FACTORS:
    #   factor_list.append(affiliation)
    # factor_list.append("student")
    # self.add_factors(factor_list)
    # self.save()
    return self

  # def get_factor_list(self):
  #   # Returns a list of factors as strings
  #   return map(lambda x: str(x), self.factor_set.all())

  # def set_factor_list(self, factor_list):
  #   for f in Factor.objects.all():
  #     if str(f) in factor_list:
  #       if not self in f.users.all():
  #         f.users.add(self)
  #     else:
  #       if self in f.users.all():
  #         f.users.remove(self)

  # def add_factors(self, factor_list):
  #   # Create any factors that haven't already been made
  #   for factor_name in factor_list:
  #     if (not Factor.objects.filter(name = factor_name).exists()
  #       and factor_name in FACTOR_LIST):
  #       new_factor = Factor.objects.create(name = factor_name)
  #       new_factor.save()

  #   # Link factors to user
  #   for f in Factor.objects.all():
  #     if (str(f) in factor_list) and (not self in f.users.all()):
  #       f.users.add(self)

  # def has_factor(self, factor_list):
  #   # Checks in the user has one of the given factors
  #   users_factors = self.get_factor_list()
  #   for f in factor_list:
  #     if f in users_factors:
  #       return True
  #   return False

  # def is_admin(self):
  #   return self.factor_set.filter(name = 'admin') != []

  def __unicode__(self):
    return "%s %s" % (self.first_name, self.last_name)

  def send_mail(self, subject, message, sender = SERVER_EMAIL):
    self.mail.send_mail(subject, message, sender, [self.email], fail_silently = False)