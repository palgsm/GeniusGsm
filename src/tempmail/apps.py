from django.apps import AppConfig


class TempmailConfig(AppConfig):
    name = 'tempmail'
    
    def ready(self):
        """Import signals when app is ready"""
        import tempmail.signals

