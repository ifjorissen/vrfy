from django.shortcuts import render
from django.http import HttpResponse

# import sys, os

from vrfy.settings import TEST
# from generic.errors import Http401
from generic.models import CSUser
# from generic.models import FACTORS

def get_user(request):
  # Get username as passed along by cosign authentication
  if TEST:
    name = 'isjoriss'
  else:
    name = request.META.get('REMOTE_USER','')

  # Check if we already have a CSUser with that username
  try:
    user = CSUser.objects.get(username = name)

  # Otherwise, try to create a new CSUser object
  except CSUser.DoesNotExist:
    user = CSUser.get_ldap_user(username = name)

  # If that fails, raise an error
  except Exception:
  	return HttpResponse('Unauthorized', status=401)
      # raise Http401('Something went wrong getting the user named %s' % name)
  return user

def authenticate(request):
  # Set the user if not already matching the cookie from Kerberos
  ru = request.META.get('REMOTE_USER', '')
  if ((request.user.username != ru) or (ru == '')):
    # Get the user and authenticating factors
    user = get_user(request).refresh_from_ldap()
    request.user = user
    return True
  # If one of the users factors is valid, return True
  # if user.has_factor(valid_factors):
  #     # Set user
  #     request.user = user
  #     return True
  # Otherwise return a 401 error
  else:
    request.user = CSUser()
    return HttpResponse('Unauthorized', status=401)
      # raise Http401(valid_factors)


def logout(request):
    if request.method != 'GET':
        raise Http404
    else:
        forward_url = request.GET.get('forward_url',
                                      'https://weblogin.reed.edu/cgi-bin/logout?http://sin.reed.edu')
        response = HttpResponsePermanentRedirect(forward_url)
        response.delete_cookie(key = 'cosign-sin')
        return response


def check_user(request):
    '''Receives a request with parameter username, returning a boolean
    indicating whether the user exists and the name of the user.'''
    username = request.GET.get('username', '')
    exists = True
    name = ''
    try:
        the_user = CSUser.objects.get(username = username)
        name = the_user.first_name + ' ' + the_user.last_name
    except CSUser.DoesNotExist:
        exists = False

    response = '{ "valid" : ' + str(exists).lower() + ', "name" : "' + name + '"}'

    return HttpResponse(response, content_type='application/json')


