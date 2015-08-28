from django.db import models
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import get_user_model
from util.query_ldap import ldap_lookup_user
import logging
log = logging.getLogger(__name__)

class LDAPRemoteUserBackend(RemoteUserBackend):
  def authenticate(self, remote_user):
    """
    The username passed as ``remote_user`` is considered trusted.  This
    method simply returns the ``User`` object with the given username,
    creating a new ``User`` object if it doesn't already exist.
    """

    if not remote_user:
      return
    user = None
    username = self.clean_username(remote_user)

    UserModel = get_user_model()

    user, created = UserModel._default_manager.get_or_create(**{
      UserModel.USERNAME_FIELD: username
    })
    if created:
      user = self.configure_user(user)

    return user

  def configure_user(self, user):
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
    log.info("UPDATE: {!s} User Profile".format(user.username))
    try:
      user_dict = ldap_lookup_user(user.username)
      try:
        user.first_name = user_dict['displayName'][0]
      except KeyError:
        user.first_name = user_dict['givenName'][0]
      user.last_name = user_dict['sn'][0]
      user.email = user_dict['mail'][0]

    except IndexError:  
      if user.is_superuser:
        log.info("No Reed Profile Found")
      else:
        log.error("Not a superuser & No Reed Profile Found ... something went terrible wrong")


    user.save()
    return user
