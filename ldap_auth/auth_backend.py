from django.db import models
from django.contrib.auth.backends import RemoteUserBackend
from vrfy.settings import TEST
import ldap3
from django.contrib.auth import get_user_model
from ldap3 import ASYNC, SYNC, ALL_ATTRIBUTES, Server, Connection, SUBTREE, ALL
 
class LDAPRemoteUserBackend(RemoteUserBackend):
  """ RemoteUserBackend for checking user/pass against REMOTE_USER
  and putting users in groups based on LDAP

  The following settings are required in settings.py:
  LDAP_SERVER='ldap://ldap.example.com'
  LDAP_SEARCH_TREE='ou=groups,dc=example,dc=com'
  LDAP_FILTER='(cn=example-django-group)'
  LDAP_FIELD='memberUid'
  ALL_USERS_GROUP=1
  """

  def authenticate(self, remote_user):
    # print("authenticate called on {!s}".format(remote_user))
    if not remote_user:
      return
    user = None
    username = self.clean_username(remote_user)
    UserModel = get_user_model()

    # Note that this could be accomplished in one try-except clause, but
    # instead we use get_or_create when creating unknown users since it has
    # built-in safeguards for multiple threads.
    if self.create_unknown_user:
      user, created = UserModel._default_manager.get_or_create(**{
          UserModel.USERNAME_FIELD: username
      })
      # if created:
      #   print("hah!")
      #   user = self.configure_user(user)
      user = self.configure_user(user)
    else:
      try:
        user = UserModel._default_manager.get_by_natural_key(username)
      except UserModel.DoesNotExist:
        pass
    return user

  def clean_username(self, username):
    return super(LDAPRemoteUserBackend, self).clean_username(username)

  def _ldap_lookup_user(self, username):
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
 
  def configure_user(self, user):
    # print("configuring user {!s}".format(user.username))
    """Set user groups and privs. 
    This method is called the first time a non-django user logs in.
    A user is created in the django database, this method
    adds the new user to the appropriate groups, and 
    sets privs. """
 
    #all remote users are staff - so they can access the admin interface
    user.is_staff=False
 
    #To determine if the user is to have further priviledges
    #we consult LDAP
 
    #connect to ldap server
    user_dict = self._ldap_lookup_user(user.username)
    try:
      user.first_name = user_dict['displayName'][0]
    except KeyError:
      user.first_name = user_dict['givenName'][0]

    user.last_name = user_dict['sn'][0]
    user.email = user_dict['mail'][0]
    user.affiliation = user_dict['eduPersonPrimaryAffiliation'][0]

    user.save()
    return user