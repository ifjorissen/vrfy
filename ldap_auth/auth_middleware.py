from django.contrib import auth
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core.exceptions import ImproperlyConfigured
from vrfy.settings import LOCAL_DEV

class LDAPRemoteUserMiddleware(RemoteUserMiddleware):
  header = "HTTP_REMOTE_USER"

  def process_request(self, request):
    username = request.META.get(self.header)

    if username is None:
      if LOCAL_DEV:
        username = 'isjoriss'

    user = auth.authenticate(remote_user=username)
    if user:
      # User is valid.  Set request.user and persist user in the session
      # by logging the user in.
      request.user = user
      auth.login(request, user)
