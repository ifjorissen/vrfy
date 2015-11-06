# from django.contrib import auth
# from django.contrib.auth.middleware import RemoteUserMiddleware
# from django.core.exceptions import ImproperlyConfigured
# from vrfy.settings import LOCAL_DEV


# class LDAPRemoteUserMiddleware(RemoteUserMiddleware):
#     header = "HTTP_REMOTE_USER"

#     def process_request(self, request):
#         username = request.META.get(self.header)
#         print(username)
#         print(request.user.username)

#         if username is None:
#             if LOCAL_DEV:
#                 username = 'isjoriss'

#         user = auth.authenticate(remote_user=username)
#         if user:
#             # User is valid.  Set request.user and persist user in the session
#             # by logging the user in.
#             request.user = user
#             auth.login(request, user)

from django.contrib import auth
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core.exceptions import ImproperlyConfigured
from vrfy.settings import LOCAL_DEV

class LDAPRemoteUserMiddleware(RemoteUserMiddleware):
  # header = "REMOTE_USER"
  def process_request(self, request):
    # AuthenticationMiddleware is required so that request.user exists.
    if not hasattr(request, 'user'):
      raise ImproperlyConfigured(
          "The Django remote user auth middleware requires the"
          " authentication middleware to be installed.  Edit your"
          " MIDDLEWARE_CLASSES setting to insert"
          " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
          " before the RemoteUserMiddleware class.")

    try:
      username = request.META[self.header]
    except KeyError:
      if LOCAL_DEV:
        username = 'isjoriss'
      # If specified header doesn't exist then remove any existing
      # authenticated remote-user, or return (leaving request.user set to
      # AnonymousUser by the AuthenticationMiddleware).
      if username != request.user.username and request.user.is_authenticated():
        self._remove_invalid_user(request)
        return
    # If the user is already authenticated and that user is the user we are
    # getting passed in the headers, then the correct user is already
    # persisted in the session and we don't need to continue.
    if request.user.is_authenticated():
      if request.user.get_username() == self.clean_username(username, request):
        return
      else:
        # An authenticated user is associated with the request, but
        # it does not match the authorized user in the header.
        self._remove_invalid_user(request)

    user = auth.authenticate(remote_user=username)
    if user:
      # User is valid.  Set request.user and persist user in the session
      # by logging the user in.
      request.user = user
      auth.login(request, user)
