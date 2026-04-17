from django.contrib.auth.apps import AuthConfig as DjangoAuthConfig


class AuthConfig(DjangoAuthConfig):
    """Custom Auth configuration with modified display name"""
    label = 'auth'
    verbose_name = 'Users And Groups'
