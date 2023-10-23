from django.apps import AppConfig
from django.db.models.signals import post_migrate


class XrpConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "xrp"

    def ready(self):
        from xrp import signals

        post_migrate.connect(signals.callback)
