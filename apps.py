from django.apps import AppConfig

class SidebarsConfig(AppConfig):
    name = 'simple_sidebars'
    verbose_name = "Sidebars and Widgets"
    
    def ready(self):
        self.module.autodiscover()