from django import template
from django.db import models
from mylibs.blogcache import BlogCache
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

register = template.Library()

Sidebar = models.get_model('simple_sidebars', 'Sidebar')
CACHE_PREFIX = "simple_sidebars_"

def find_sidebar(parser, token, Node):    
    # split_contents() knows not to split quoted strings.
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
       self.cache_time = cache_time
       self.cache_key = self.CACHEPREFIX + key
    
    def render_sidebar(self, sidebar):
        raise NotImplementedError
    
    def render(self, context):
        try:
            if self.cache_time:
                blogcache = BlogCache(self.cache_key)
                result = blogcache.get()
                if not result:
                    sidebar = Sidebar.objects.get(title=self.key)
                    result = self.render_sidebar(sidebar)
                    blogcache.set(result)
                return result
            else:
                sidebar = Sidebar.objects.get(title=self.key)
                return self.render_sidebar(sidebar)
        except Sidebar.DoesNotExist:
            return mark_safe(u'<div class="error">Sidebar Could Not Be Found.</div>')

class RenderNode(SidebarNode):
    CACHEPREFIX = 'simplesidebar_'
            
    def render_sidebar(self, sidebar):
        result = mark_safe(sidebar.render())
        return result

class MediaNode(SidebarNode):
    CACHEPREFIX = 'simplemedia_'
    
    def render_sidebar(self, sidebar):
        result = mark_safe(sidebar.render_media())
        return result

def get_sidebar_render(parser, token):
    return find_sidebar(parser, token, RenderNode)

def get_sidebar_media(parser, token):
    return find_sidebar(parser, token, MediaNode)

register.tag('simple_sidebar', get_sidebar_render)
register.tag('sidebar_media', get_sidebar_media)
