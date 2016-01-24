from django.apps import AppConfig
import logging
log = logging.getLogger(__name__)

class CourseConfig(AppConfig):
    name = 'course'
    verbose_name = "Assignment Administration"

    def ready(self):
        log.info("Assignment READY!")
        from . import receivers