from django.apps import AppConfig


class ControlPinConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'control_pin'

    def ready(self):
        from .schedular import start_scheduler
        start_scheduler()