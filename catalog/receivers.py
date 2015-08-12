from django.dispatch import receiver
from course import models
from catalog.models import Reedie
from django.db.models.signals import post_save, pre_init
from django.contrib.auth.models import User
from util.query_ldap import ldap_lookup_user


@receiver(post_save, sender=User)
def User_post_save(sender, **kwargs):
  print(sender)
  user = kwargs.get("instance")
  print("post_save!!!")
  print(user.username)
  try:
    user_dict = ldap_lookup_user(user.username)
    reed_usr, created = Reedie.objects.get_or_create(user=user)
    reed_usr.role = user_dict['eduPersonPrimaryAffiliation']
    reed_usr.save()
  except IndexError:  
    if user.is_superuser:
      print("superusers don't need to be reedies")
    else:
      print("could not find a reedie with that username")
