from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AppEscolarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App_Escolar'

    def ready(self):
        import App_Escolar.signals
