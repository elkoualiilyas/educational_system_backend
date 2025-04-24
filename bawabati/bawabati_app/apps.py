from django.apps import AppConfig

class BawabatiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bawabati_app'
    
    def ready(self):
        import bawabati_app.signals 