from django.dispatch import receiver
from course import models
from catalog.models import Reedie
from django.db.models.signals import post_save, post_init
from django.contrib.auth.models import User
from util.query_ldap import ldap_lookup_user
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out


@receiver(post_save, sender=User)
def User_post_save(sender, **kwargs):
  # logger = logging.getLogger(__name__)
  user = kwargs.get("instance")
  try:
    user_dict = ldap_lookup_user(user.username)
    reed_usr, created = Reedie.objects.get_or_create(user=user)
    reed_usr.role = user_dict['eduPersonPrimaryAffiliation']
    reed_usr.last_updated = timezone.now()
    reed_usr.save()
  except IndexError:  
    if user.is_superuser:
      print("superusers don't need to be reedies")
    else:
      print("could not find a reedie with that username")


@receiver(user_logged_in)
def sig_user_logged_in(sender, user, request, **kwargs):
  print(sender)
  logger = logging.getLogger(__name__)
  logger.info("user logged in: %s at %s" % (user, request.META['REMOTE_ADDR']))


@receiver(user_logged_out)
def sig_user_logged_out(sender, user, request, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info("user logged out: %s at %s" % (user, request.META['REMOTE_ADDR']))