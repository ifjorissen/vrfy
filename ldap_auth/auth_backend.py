from django.db import models
from django.contrib.auth.backends import RemoteUserBackend
from vrfy.settings import TEST
from django.contrib.auth import get_user_model
from util.query_ldap import ldap_lookup_user
 
class LDAPRemoteUserBackend(RemoteUserBackend):
  def authenticate(self, remote_user):
    """
    The username passed as ``remote_user`` is considered trusted.  This
    method simply returns the ``User`` object with the given username,
    creating a new ``User`` object if ``create_unknown_user`` is ``True``.

    Returns None if ``create_unknown_user`` is ``False`` and a ``User``
    object with the given username is not found in the database.
    """
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
      if created:
        user = self.configure_user(user)
    else:
      try:
        user = UserModel._default_manager.get_by_natural_key(username)
      except UserModel.DoesNotExist:
        pass
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
        print("superusers can be configured without being reedies")
      else:
        print("could not find a reedie with that username")

    user.save()
    return user