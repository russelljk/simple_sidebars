import re
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from simple_sidebars.utils import generate_classes


class OptionDoesNotExist(ObjectDoesNotExist):
    pass


class WidgetManager(object):
    """
    Manager class that contains all registered widgets.
    """
    valid_widget_name = re.compile(r'^[a-z_\-][a-z0-9_\-]*$')

    def __init__(self, base_class):
        self.widgets = {}
        self._WidgetClass = base_class

    def register(self, n, w=None):
        if isinstance(w, self._WidgetClass.__class__) and WidgetManager.valid_widget_name.match(n):
            self.widgets[n] = w

    def lookup(self, n):
        return self.widgets[n]

    def exists(self, n):
        return self.widgets.has_key(n)

    def items(self):
        return self.widgets.items()

    def get_form(self, k):
        if self.widgets.has_key(k):
            _Class = self.lookup(k)
            return _Class.widget_form


class WidgetOption(object):
    '''
    WidgetOption is the base option class for widgets. Options are added to widgets
    in the same way as Fields are added to Django Models.

    Create a new Widget instance and the add the options as class variables.

    For Example:

        class MyWidget(Widget):
            name = CharOption(required=True)
            email = EmailOption(default='contact@example.com')
            ...

    Like a Django model you can then you can access the values via instances of the Widget.

    my_widget.name
    my_widget.email

    '''
    creation_counter = 0

    def __init__(self, required=False, default=None, kind=str, name=None, max_length=200, help_text=u""):
        self.creation_order = WidgetOption.creation_counter
        WidgetOption.creation_counter += 1
        self.first_widget = False
        self.last_widget = False
        self.default = default
        self.required = required
        self.kind = kind
        self.name = name
        self.max_length = max_length
        self.label = None
        self.help_text = help_text
        self.make_label()

    def get_kwargs(self):
        return {
            "label": self.label,
            "required":self.required,
            "initial": self.default,
        }

    def get_field(self):
        kwargs = self.get_kwargs()
        return forms.CharField(max_length=self.max_length, **kwargs)

    def make_label(self):
        if self.name:
            self.label = self.name.replace('_', ' ').title()

    def set_name(self, name):
        if self.name is None:
            self.name = name
            self.make_label()

    def get_value(self, name, options):
        if hasattr(options, name):
            return getattr(options, name)
        return self.default

    def parse_option(self, key, options):
        if not key in options:
            if self.required:
                raise OptionDoesNotExist('Option "{0}" not found.'.format(key))
            else:
                return self.default
        return options[key]

"""
Just an alias for WidgetOption.
"""
class CharOption(WidgetOption):
    pass


class IntegerOption(WidgetOption):
    def get_field(self):
        kwargs = self.get_kwargs()
        return forms.IntegerField(**kwargs)


class URLOption(WidgetOption):
    def get_field(self):
        kwargs = self.get_kwargs()
        return forms.URLField(**kwargs)


class EmailOption(WidgetOption):
    def get_field(self):
        kwargs = self.get_kwargs()
        return forms.EmailField(**kwargs)


class BooleanOption(WidgetOption):
    def get_field(self):
        kwargs = self.get_kwargs()
        return forms.BooleanField(**kwargs)


class ModelSelectOption(WidgetOption):
    def __init__(self, *args, **kwargs):
        queryset = kwargs['queryset']
        kwargs.pop('queryset')
        super(ModelSelectOption, self).__init__(*args, **kwargs)
        self.queryset = queryset

    def get_value(self, name, options):
        if hasattr(options, name):
            instance = getattr(options, name)
            return instance.pk
        return self.default

    def parse_option(self, key, options):
        pk = super(ModelSelectOption, self).parse_option(key, options)
        if isinstance(pk, self.queryset.model):
            return pk
        return self.queryset.model.objects.get(pk=pk)

    def get_field(self):
        args = {
            'queryset':self.queryset,
            'required':self.required,

        }

        if self.default:
            args['initial'] = self.default

        return forms.ModelChoiceField(**args)


class TextOption(WidgetOption):
    def __init__(self, attrs={'rows': 5, 'cols': 60}, *args, **kwargs):
        super(TextOption, self).__init__(*args, **kwargs)
        self.attrs = attrs

    def get_field(self):
        field = super(TextOption, self).get_field()
        field.widget = forms.Textarea(attrs=self.attrs)
        return field


class WidgetBase(type):
    widget_manager = None

    def __new__(cls, name, bases, attrs):
        super_new = super(WidgetBase, cls).__new__
        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})

        options = {}

        for b in bases:
            if hasattr(b, 'options'):
                options.update(getattr(b, 'options'))

        for key, val in attrs.items():
            if isinstance(val, WidgetOption):
                val.set_name(key)
                options[key] = val
            else:
                new_class.add_to_class(key, val)

        if not 'widget_kind' in attrs:
            new_class.add_to_class('widget_template', new_class.__name__.lower())

        if not 'widget_template' in attrs:
            new_class.add_to_class('widget_template', 'simple_widgets/base.html')

        if not cls.widget_manager:
            cls.widget_manager = WidgetManager(new_class)
        else:
            cls.widget_manager.register(new_class.widget_kind, new_class)

        new_class.add_to_class('options', options)
        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class Widget(object):
    __metaclass__ = WidgetBase
    title = CharOption(required=False, default=u'', help_text=_("The title to be displayed above the widget."))
    html_classes = TextOption(required=False, default=u'', help_text=_("Comma separated list of css classes to apply to the widget."))
    show_title = BooleanOption(required=False, default=True, help_text=_("Determines if the widget's title is visible."))
    template_path = TextOption(required=False, default=u'', help_text=_("Full path to the template which will be used to render the widget. Leave blank to use to default."))

    def get_default_classes(self):
        return ['widget', self.widget_kind + '-widget']

    def get_classes(self):
        cls = generate_classes(self.html_classes)
        if cls == None:
            cls = []
        cls += self.get_default_classes()

        res = ' '.join(cls)
        return res

    classes = property(get_classes)

    def __init__(self, args, add=False):
        self._options = args

        if add:
            for name, option in self.__class__.options.items():
                value = option.default
                setattr(self, name, value)
        else:
            for name, option in self.__class__.options.items():
                value = option.parse_option(name, self._options)
                setattr(self, name, value)

    def parse_option(self, key, default=None):
        if key in self.options:
            return self.options[key]
        return default

    def get_schema_data(self):
        data = { 'kind': self.widget_kind }
        for name, option in self.options.items():
            data[name] = option.get_value(name, self)
        return data

    def make_form(self):
        attrs = {}
        items = self.options.items()

        def options_key(a):
            return a[1].creation_order

        items = sorted(items, key=options_key)

        for v, o in items:
            attrs[ o.name ] = o.get_field()

        return type('_WidgetForm', (forms.Form,), attrs)

    def update_options(self, data):
        for name, option in self.options.items():
            value = option.parse_option(name, data)
            setattr(self, name, value)

    def render(self, context=None):
        data = {
            'widget': self
        }

        if context is not None:
            request = context.get('request', None)
            if request:
                data['request'] = request

        if self.template_path:
            template = self.template_path
        else:
            template = self.widget_template
        return render_to_string(template, data)

    def get_options(self):
        pass
