from django.apps import AppConfig


class Dof3ABaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dof3a_base'

    def ready(self):
        import dof3a_base.signals