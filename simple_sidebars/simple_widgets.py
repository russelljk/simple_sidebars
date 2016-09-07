from simple_sidebars import widgets
from django.utils.safestring import mark_safe


class FollowWidget(widgets.Widget):
    """
    Example widget which shows you how to create your own.
    """

    # The type of widget, needs to unique across all your apps.
    # It is shown in the admin when selecting a widget.
    widget_kind = 'follow'

    # The template used to render this widget. See the template below and the base.html template to see
    # how to render your widget. You can override this in the admin on a widget-by-widget basis.
    widget_template = 'simple_widgets/follow.html'

    # Options that will appear in the admin and be a part of the widget instance. This is similiar to
    # how models work and should be familiar to Django developers.
    email = widgets.EmailOption(max_length=255, required=False)
    twitter_name = widgets.CharOption(max_length=255, required=False)
    facebook_url = widgets.URLOption(max_length=255, required=False)
    google_plus_url = widgets.URLOption(max_length=255, required=False)
    youtube_url = widgets.URLOption(max_length=255, required=False)
    rss_view = widgets.CharOption(max_length=100, required=False)
    atom_view = widgets.CharOption(max_length=100, required=False)
    github_name = widgets.CharOption(max_length=255, required=False)

    # Below are properties that belong to our widget.
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

    def get_github_url(self):
        if self.github_name:
            return 'http://github.com/{0}/'.format(self.github_name)
        return None

    github_url = property(get_github_url)
