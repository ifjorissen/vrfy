from django.apps import AppConfig
import logging
log = logging.getLogger(__name__)

class CatalogConfig(AppConfig):
    name = 'catalog'
    verbose_name = "Catalog Administration"

    def ready(self):
        log.info("CATALOG READY!")