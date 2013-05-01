import re
from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.template.loader import render_to_string

class OptionDoesNotExist(ObjectDoesNotExist):
    pass

class WidgetManager(object):
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
    creation_counter = 0
    
    def __init__(self, required=False, default=None, kind=str, name=None, max_length=200):
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
        self.make_label()
    
    def get_field(self):
        return forms.CharField(label=self.label, max_length=self.max_length, required=self.required, initial=self.default)
    
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

class TextWidget(WidgetOption):
    def get_field(self):
        field = super(TextWidget, self).get_field()
        field.widget = forms.Textarea()
        return field

class IntegerOption(WidgetOption):
    def get_field(self):
        return forms.IntegerField(label=self.label, required=self.required, initial=self.default)

class URLOption(WidgetOption):
    def get_field(self):
        return forms.URLField(label=self.label, required=self.required, initial=self.default)

class EmailOption(WidgetOption):
    def get_field(self):
        return forms.EmailField(label=self.label, required=self.required, initial=self.default)
        
class BooleanOption(WidgetOption):
    def get_field(self):
        return forms.BooleanField(label=self.label, required=self.required, initial=self.default)
        
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
    def get_field(self):
        field = super(TextOption, self).get_field()
        field.widget = forms.Textarea(attrs={'rows':5, 'cols':60})
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
    title = WidgetOption(required=False, default='')
    css_classes = TextOption(required=False, default='')
    show_title = BooleanOption(required=False, default=True)
    template_path = TextOption(required=False, default='')
    
    def default_classes(self):
        return ['widget', self.widget_kind + '-widget']
        
    def get_classes(self):
        cls = self.css_classes.split(',')        
        if cls == None:
            cls = []
        cls += self.default_classes()
                
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
    
    def render(self):
        data = {
            'widget': self,
        }
        
        if self.template_path:
            template = self.template_path
        else:
            template = self.widget_template
        return render_to_string(template, data)
    
    def get_options(self):
        pass