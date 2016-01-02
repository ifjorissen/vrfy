from django.apps import AppConfig
import logging
log = logging.getLogger(__name__)


class LDAPAuthConfig(AppConfig):
    name = 'ldap_auth'
    verbose_name = "Authentication With LDAP"

    def ready(self):
        log.info("LDAP_auth READY!")
        from . import receivers
