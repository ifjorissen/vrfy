from django.dispatch import receiver
from course import models
from catalog.models import Reedie
from django.db.models.signals import post_save, post_init
from django.contrib.auth.models import User
from util.query_ldap import ldap_lookup_user
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
import logging

log = logging.getLogger(__name__)

@receiver(user_logged_in, sender=User)
def sig_user_logged_in(sender, user, request, **kwargs):
    log.info(
        "LOGIN: {} @ {}".format(
            user.username,
            request.META['REMOTE_ADDR']))
    print("ok logged in")
    # log.info("UPDATE: {!s} Reed Profile".format(user.username))
    try:
        user_dict = ldap_lookup_user(user.username)
        reed_usr, created = Reedie.objects.get_or_create(user=user)
        reed_usr.role = user_dict['eduPersonPrimaryAffiliation']
        reed_usr.last_updated = timezone.now()
        reed_usr.save()
    except IndexError:
        if user.is_superuser:
            log.info("No Reed Profile Found")
        else:
            log.error(
                "Not a superuser & No Reed Profile Found ... something went terrible wrong")


@receiver(user_logged_out, sender=User)
def sig_user_logged_out(sender, user, request, **kwargs):
    log.info(
        "LOGOUT: {} @ {}".format(
            user.username,
            request.META['REMOTE_ADDR']))
