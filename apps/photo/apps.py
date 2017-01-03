from django.apps import AppConfig


class PhotoConfig(AppConfig):
    name = 'apps.photo'

    def ready(self):
        import apps.photo.signals

