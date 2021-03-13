from django.apps import AppConfig


class PlatformusersConfig(AppConfig):
    name = "platformUsers"

    def ready(self):
        import platformUsers.signals
