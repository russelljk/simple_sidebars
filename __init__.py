
def autodiscover():
    module_name = 'simple_widgets'
    import imp
    import sys
    from django.utils.importlib import import_module
    
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            import_module(app)
            app_path = sys.modules[app].__path__
        except AttributeError:
            continue
        try:
            imp.find_module(module_name, app_path)
        except ImportError:
            continue
        import_module('%s.%s' % (app, module_name))
        app_path = sys.modules['%s.%s' % (app, module_name)]

default_app_config = 'simple_sidebars.apps.SidebarsConfig'