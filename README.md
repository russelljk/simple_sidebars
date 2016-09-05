# Simple Sidebars

A relatively simple, easy to use but powerful widget and sidebar system for Django.


## Setup

Simply add `simple_sidebars` to your installed apps:

```python
INSTALLED_APPS = (
	...
	'simple_sidebars',
	...
)
```

Then run migrations:

	./manage.py migrate


### Using Sidebars

Now you need to create sidebars and add widgets to them.

 1. Find **Sidebars and Widgets** in the administration site.
 2. Select an existing Sidebar or add a new Sidebar and enter the Title.
 3. Optionally specify a template name. This template will be used to render the sidebar. See the section on Customization for more information.
 4. Optionally specify one or more CSS classes to apply to the sidebar. They must be comma separated and may contain the following characters: a-z, A-Z, 0-9, -, +
 5. Save/Create and start adding widgets.


### Using Widgets

Widgets are assigned to sidebars. Find the section called Sidebar Widgets. Select the widget name from the list. Press "Add an widget".

Like sidebars widgets have a Title, CSS Classes, Template Path.

They also have a Show Title option. The title is required but you can hide it by unchecking Show Title.

The rest of the options are specific the the widget.


### Creating Widgets

Widgets are loaded from `simple_widgets.py` file located in an installed app. Any Widget derived class will be loaded as a widget and be available in the admin site.

```python
from simple_sidebars import widgets

class MyWidget(widgets.Widget):
    widget_kind = 'mywidget' # The name of our widget as shown in the admin. Must be unique.
    widget_template = 'app/simple_widgets/mywidget.html' # Our template that renders the widget.
```

Since the widget is passed to the template when rendered you can add methods, properties and attributes to help you render the widget.

You can also add custom options which can be set in the admin to control how the widget is displayed and what information is rendered.


#### Widget Options

```python
class FollowWidget(widgets.Widget):
    widget_kind = 'follow'
    widget_template = 'simple_widgets/follow.html'

    email = widgets.EmailOption(max_length=255, required=False)
    twitter_name = widgets.CharOption(max_length=255, required=False)
    facebook_url = widgets.URLOption(max_length=255, required=False)
    google_plus_url = widgets.URLOption(max_length=255, required=False)
    youtube_url = widgets.URLOption(max_length=255, required=False)
    rss_view = widgets.CharOption(max_length=100, required=False)
    atom_view = widgets.CharOption(max_length=100, required=False)
    github_name = widgets.CharOption(max_length=255, required=False)
    atom_view = widgets.CharOption(max_length=100, required=False)
    github_name = widgets.CharOption(max_length=255, required=False)
```

Above is the example FollowWidget included with Simple Sidebars. As you can see Options are added in the same manner as Django's models and forms fields.

The following is a list of provided options and equivalent form field:

 * CharOption (*forms.CharField*)
 * TextOption (*forms.Textarea*)
 * EmailOption (*forms.EmailField*)
 * IntegerOption (*forms.IntegerField*)
 * URLOption (*forms.URLField*)
 * BooleanOption (*forms.BooleanField*)
 * ModelSelectOption (*forms.ModelChoiceField*)

You can create your own Option by deriving from WidgetOption. If there is an existing Django form field then it's fairly easy. See widgets.py for examples.
