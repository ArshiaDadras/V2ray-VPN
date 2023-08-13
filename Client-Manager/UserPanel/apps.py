from django.apps import AppConfig
from django.conf import settings


class UserpanelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "UserPanel"

    def ready(self):
        if settings.SCHEDULER_AUTOSTART:
            from . import scheduler
            scheduler.start()
