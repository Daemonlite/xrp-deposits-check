from wallets.settings import REDIS
import json
from django.core.serializers.json import DjangoJSONEncoder
import logging

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, cls, template):
        self.cls = cls
        self.template = template

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
        if REDIS.get(self.template):
            self.save_values()
        else:
            self.save_values()
