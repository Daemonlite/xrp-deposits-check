from wallets.settings import REDIS
import json
from django.core.serializers.json import DjangoJSONEncoder
import logging
from django.dispatch import receiver
from django.db.models.signals import post_migrate


logger = logging.getLogger(__name__)

class Cache:
    def __init__(self, cls, template):
        self.cls = cls
        self.template = template

        # Connect the post_migrate signal to the handle_migrations method
        post_migrate.connect(self.handle_migrations, sender=self.cls)

    def save_values(self):
        try:
            values = self.cls.objects.all().values()
            values_list = list(values)
            json_data = json.dumps(values_list, cls=DjangoJSONEncoder)
            REDIS.set(self.template, json_data)
        except Exception as e:
            logger.warning(str(e))
            logger.warning(f"failed to save cache data")

    def fetch_values(self):
        try:
            json_data = json.loads(REDIS.get(self.template))
            return json_data
        except Exception as e:
            logger.warning(str(e))
            self.save_values()
            json_data = json.loads(REDIS.get(self.template))
            return json_data

    def handle_migrations(self, **kwargs):
        # Check if the cache key exists and invalidate it
        if REDIS.get(self.template):
            REDIS.delete(self.template)