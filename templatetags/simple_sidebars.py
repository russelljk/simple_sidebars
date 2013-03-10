from django import template
from django.db import models
from mylibs.blogcache import BlogCache
from django.utils.safestring import mark_safe

register = template.Library()

Sidebar = models.get_model('simple_sidebars', 'Sidebar')
CACHE_PREFIX = "simple_sidebars_"

def do_get_sidebar(parser, token):    
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
    return SidebarNode(sidebar_title[1:-1], cache_time)

from django.template.loader import render_to_string

class SidebarNode(template.Node):
    def __init__(self, key, cache_time=0):
       self.key = key
       self.cache_time = cache_time
       self.cache_key = CACHE_PREFIX + key
       
    def render(self, context):
        try:
            if self.cache_time:
                blogcache = BlogCache(self.cache_key)
                result = blogcache.get()
                if not result:
                    sidebar = Sidebar.objects.get(title=self.key)
                    result = mark_safe(sidebar.render())
                    blogcache.set(result)
                return result
            else:
                sidebar = Sidebar.objects.get(title=self.key)
                return mark_safe(sidebar.render())
        except Sidebar.DoesNotExist:
            return mark_safe(u'<div class="error">Sidebar Couldnot be Found</div>')
            
register.tag('simple_sidebar', do_get_sidebar)
