
from django.apps import AppConfig
# from ldap_auth.apps import LDAPAuthConfig
# from course.apps import CourseConfig

# class AuthConfig(LDAPAuthConfig):
#   verbose_name = "Authentication"


class LDAPAuthConfig(AppConfig):
  name = 'ldap_auth'
  verbose_name = "Authentication With LDAP"

  def ready(self):
    print("LDAP_auth READY!")
    import ldap_auth.receivers

class CourseConfig(AppConfig):
  name = 'course'
  verbose_name = "Assignment Administration"

  def ready(self):
    print("Assignment READY!")
    import course.receivers

class CatalogConfig(AppConfig):
  name = 'catalog'
  verbose_name = "Catalog Administration"

  def ready(self):
    print("CATALOG READY!")
