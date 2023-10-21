from django.apps import AppConfig
from django.db.models.signals import post_migrate

class XrpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xrp"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals

        # Explicitly connect a signal handler.
        post_migrate.connect(signals.my_callback)