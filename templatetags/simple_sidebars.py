from django import template
from django.db import models
from mylibs.helpers.caching import cache_safe_set, cache_safe_get
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.cache import cache
register = template.Library()

Sidebar = models.get_model('simple_sidebars', 'Sidebar')
CACHE_PREFIX = "simple_sidebars_"

def find_sidebar(parser, token, Node):
    tokens = token.split_contents()
    sidebar_title = 5
    cache_time = 0
    
    tokens = token.split_contents()
    if len(tokens) < 2 or len(tokens) > 3:
        raise template.TemplateSyntaxError, "%r tag should have either 2 or 3 arguments" % (tokens[0],)
    if len(tokens) == 2:
        tag_name, sidebar_title = tokens
        cache_time = 0
    if len(tokens) == 3:
        tag_name, sidebar_title, cache_time = tokens
    
    # Check to see if the sidebar_title is properly double/single quoted
    if not (sidebar_title[0] == sidebar_title[-1] and sidebar_title[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    
    # Send sidebar_title without quotes and caching time
    return Node(sidebar_title[1:-1], cache_time)

def get_sidebar(parser, token):
    # Usage: {% get_sidebar 'Sidebar Name' as 'VariableName' %}
    
    tokens = token.split_contents()
    
    if len(tokens) != 4:
        raise template.TemplateSyntaxError, "%r tag should have 3 arguments" % (tokens[0],)
    
    lookup, skip, var_name = tokens[1:]
        
    if skip != 'as':
        raise template.TemplateSyntaxError, "%r tag's second argument should be as without quotes."
            
    if (not is_quoted(lookup)) or (not is_quoted(var_name)):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tokens[0]
    
    lookup = lookup[1:-1]
        
    return GetSidebar(lookup, var_name[1:-1])

class GetSidebar(template.Node):
    def __init__(self, lookup, option, var_name):
        self.lookup = lookup
        self.var_name = var_name
    
    def render(self, context):
        try:
            x = Sidebar.objects.get(title=self.lookup)
        except:
            x = None
        context[self.var_name] = x            
        return ''

@register.filter
def get_sidebar(key):
    try:
        sidebar = Sidebar.objects.get(title=key)
        return sidebar
    except:
        return None

class SidebarNode(template.Node):
    def __init__(self, key, cache_time=0):
       self.key = key
       self.cache_time = int(cache_time)
       self.request = None
       self.cache_key = self.CACHEPREFIX + key
    
    def render_sidebar(self, sidebar):
        raise NotImplementedError
    
    def render(self, context):
        self.request = context.get('request', None)
        
        try:
            if self.cache_time > 0:
                result = cache_safe_get(self.cache_key)
                
                if not result:
                    sidebar = Sidebar.objects.get(title=self.key)
                    result = self.render_sidebar(sidebar)
                    cache_safe_set(self.cache_key, result, 1800)
                return mark_safe(result)
            else:
                sidebar = Sidebar.objects.get(title=self.key)
                return mark_safe(self.render_sidebar(sidebar))
        except Sidebar.DoesNotExist:
            return mark_safe(u'<div class="error">Sidebar Could Not Be Found.</div>')

class RenderNode(SidebarNode):
    CACHEPREFIX = 'simplesidebar:'
    
    def render_sidebar(self, sidebar):
        result = sidebar.render(self.request)
        return result

class MediaNode(SidebarNode):
    CACHEPREFIX = 'simplesidebar_media:'
    
    def render_sidebar(self, sidebar):
        result = sidebar.render_media()
        return result

def get_sidebar_render(parser, token):
    return find_sidebar(parser, token, RenderNode)

def get_sidebar_media(parser, token):
    return find_sidebar(parser, token, MediaNode)

register.tag('simple_sidebar',  get_sidebar_render)
register.tag('sidebar_media',   get_sidebar_media)
register.tag('get_sidebar',     get_sidebar)

@register.simple_tag(takes_context=True)
def render_widget(context, widget):
    return widget.render(context)