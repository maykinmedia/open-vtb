from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    name = "openvtb.accounts"

    def ready(self):
        from . import signals  # noqa

        post_migrate.connect(signals.update_admin_index, sender=self)
