from django.apps import AppConfig


class SpeedEthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "speed_eth"

    def ready(self):
        import speed_eth.signals
