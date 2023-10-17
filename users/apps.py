from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    # Gio: I thought this was necessary, but it seems it is not
    # def ready(self):
        # import users.signals
