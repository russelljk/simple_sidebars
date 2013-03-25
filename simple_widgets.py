from simple_sidebars import widgets

class FollowWidget(widgets.Widget):
    widget_kind = 'follow'
    widget_template = 'simple_widgets/follow.html'
    
    def get_rss_url(self):
        if self.rss_view:
            from django.core.urlresolvers import reverse
            return reverse(self.rss_view)
        return None
    
    rss_url = property(get_rss_url)
    
    def get_atom_url(self):
        if self.atom_view:
            from django.core.urlresolvers import reverse
            return reverse(self.atom_view)
        return None
    
    atom_url = property(get_atom_url)
    
    twitter_name = widgets.WidgetOption(max_length=255, required=False)
    facebook_url = widgets.URLOption(max_length=255, required=False)
    rss_view = widgets.WidgetOption(max_length=100, required=False)
    atom_view = widgets.WidgetOption(max_length=100, required=False)