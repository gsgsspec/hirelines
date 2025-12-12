import os
from django.apps import AppConfig


class AppApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_api'
    
    # def ready(self):
    #     if os.environ.get("RUN_MAIN") in ("true", "True"):   
    #         from app_api.functions.email_resume import processEmailsFetch

    #         processEmailsFetch()
