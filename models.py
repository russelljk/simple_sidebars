from __future__ import unicode_literals

import json
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from simple_sidebars.utils import generate_classes
from simple_sidebars.widgets import WidgetBase


class WidgetDoesNotExist(ObjectDoesNotExist):
    pass


'''
Sidebar model which can contain multiple widgets.
'''
class Sidebar(models.Model):
    def __init__(self, *args, **kwargs):
        super(Sidebar, self).__init__(*args, **kwargs)
        self.widgets = []
        self.schema = {}
        self.load_schema()

    title = models.CharField(max_length=300, unique=True, help_text=_("Title of this sidebar."))
    template = models.CharField(max_length=300, blank=True, null=True, default=None, help_text=_("Full path to a custom template to use to render this sidebar. If blank the default is used."))
    widget_schema = models.TextField(blank=True, default='')
    html_classes = models.TextField("HTML classes", validators=[validators.RegexValidator(regex=r'^[a-zA-Z0-9_\-\s,]+$')], blank=True, null=True, help_text=_("Comma separated list of HTML classes for the sidebar."))
    html_id = models.SlugField("HTML id", max_length=300, blank=True, null=True, default=None, help_text=_("The HTML id to use for the sidebar."))
    version = models.PositiveIntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.title + ' (widgets: ' + str(len(self.widgets)) + ')'

    def get_classes(self):
        cls = generate_classes(self.html_classes)
        res = ' '.join(cls)
        return res

    classes = property(get_classes)

    def is_version(self, version):
        try:
            version = int(version)
            return self.version == version
        except:
            return False

    def load_schema(self):
        if not self.widget_schema:
            return

        self.schema = json.loads( self.widget_schema )
        pos = 1
        for option in self.schema:
            name = option['kind']
            _WidgetClass = WidgetBase.widget_manager.lookup(name)
            w = _WidgetClass(option)
            w.position = pos
            self.widgets.append(w)
            pos += 1

        if self.widgets:
            self.widgets[0].first_widget = True
            self.widgets[-1].last_widget = True

    def save_schema(self):
        schema = []
        for w in self.widgets:
            schema.append( w.get_schema_data() )
        self.widget_schema = json.dumps(schema)

        return self.widget_schema

    def get_widget(self, i):
        return self.widgets[i]

    def add_widget(self, w):
        self.widgets.append(w)

    def remove_widget(self, w):
        try:
            del self.widgets[w]
        except:
            raise WidgetDoesNotExist('Cannot delete widget {0}.'.format(w))

    def save(self, *args, **kwargs):
        self.save_schema()
        self.version += 1
        return super(Sidebar, self).save(*args, **kwargs)

    def get_item_types(self):
        from simple_sidebars.widgets import WidgetBase
        items = [x for x, y in WidgetBase.widget_manager.items()]
        return items

    def render_media(self, css=True, js=True):
        '''
        Renders all css and js media in this widget.
        '''
        all_js = []
        all_css = []
        for widget in self.widgets:
            if hasattr(widget, 'Media'):
                _Media = widget.Media
                if js and hasattr(_Media, 'js'):
                    for js in _Media.js:
                        all_js.append( '<script type="text/javascript" src="{0}"></script>'.format(js) )
                if css and hasattr(_Media, 'css'):
                    for media in _Media.css:
                        for css in _Media.css[media]:
                            all_css.append('<link rel="stylesheet" type="text/css" media="{0}" href="{1}" />'.format(media, css))
        return mark_safe(''.join(all_js + all_css))

    def render(self, request=None):
        template_name = self.template if self.template else 'simple_sidebars/base.html'
        return render_to_string(template_name, { 'sidebar': self, 'widgets': self.widgets, 'request': request })
