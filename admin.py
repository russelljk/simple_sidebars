from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.conf.urls import url
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.templatetags.static import static
from django.utils.translation import ugettext as _
from simple_sidebars.models import Sidebar


class SidebarAdmin(admin.ModelAdmin):
    exclude = ('widget_schema',)

    def get_urls(self):
        urls = super(SidebarAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<sidebar_pk>[-\w]+)/items/add/$', self.admin_site.admin_view(self.add_sidebar_item), name='simple_sidebars_sidebar_additem'),
            url(r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/$', self.admin_site.admin_view(self.edit_sidebar_item), name='simple_sidebars_sidebar_edititem'),
            url(r'^(?P<sidebar_pk>[-\w]+)/version_mismatch/$', self.admin_site.admin_view(self.version_mismatch), name='simple_sidebars_sidebar_version_mismatch'),
            url(r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/delete/$', self.admin_site.admin_view(self.delete_sidebar_item), name='simple_sidebars_sidebar_deleteitem'),
            url(r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/move_up/$', self.admin_site.admin_view(self.move_up_item), name='simple_sidebars_sidebar_upitem'),
            url(r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/move_down/$', self.admin_site.admin_view(self.move_down_item), name='simple_sidebars_sidebar_downitem'),
        ]
        return my_urls + urls

    def check_permissions_for_object(self, request, model, obj_pk):
        '''
        Helper function that returns a sidebar/sidebaritem if it exists
        and if the user has the correct permissions.

        Since we need to do this for every method
        '''
        try:
            obj = model._default_manager.get(pk=obj_pk)
        except model.DoesNotExist:
            obj = None

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj is None:
            raise Http404('%s object with primary key %r does not exist.' % (model.__name__, escape(obj_pk)))
        return obj

    def edit_sidebar_item(self, request, sidebar_pk, widget_id):
        sidebar = self.check_permissions_for_object(request, Sidebar, sidebar_pk)
        widget_id = int(widget_id)
        widget = sidebar.get_widget(widget_id)
        _WidgetForm = widget.make_form()

        if request.method == "POST":
            form = _WidgetForm(request.POST)
            if form.is_valid():
                version = request.POST['sidebar_version']
                if not sidebar.is_version(version):
                    return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_version_mismatch', args=[sidebar_pk]))
                widget.update_options(form.cleaned_data)
                sidebar.save()
                return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_change', args=[sidebar_pk]))
        else:
            form = _WidgetForm(widget.get_schema_data())
        kind = widget.widget_kind
        return render(request, 'admin/simple_sidebars/sidebar/widget_add.html', { 'kind':kind, 'form': form, 'sidebar': sidebar, 'widget': widget})

    def version_mismatch(self, request, sidebar_pk):
        sidebar = self.check_permissions_for_object(request, Sidebar, sidebar_pk)
        return render(request, 'admin/simple_sidebars/sidebar/version_mismatch.html', { 'sidebar': sidebar, })

    def add_sidebar_item(self, request, sidebar_pk):
        sidebar = self.check_permissions_for_object(request, Sidebar, sidebar_pk)
        if request.method == "POST":
            kind = request.POST['kind']
        else:
            kind = request.GET['kind']
        from simple_sidebars.widgets import WidgetBase

        widgetclass = WidgetBase.widget_manager.lookup(kind)
        widget = widgetclass({}, add=True)
        _WidgetForm = widget.make_form()

        if request.method == "POST":
            form = _WidgetForm(request.POST)
            if form.is_valid():
                version = request.POST['sidebar_version']
                if not sidebar.is_version(version):
                    return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_version_mismatch', args=[sidebar_pk]))
                widget.update_options(form.cleaned_data)
                sidebar.add_widget(widget)
                sidebar.save()
                return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_change', args=[sidebar_pk]))
        else:
            form = _WidgetForm()

        return render(request, 'admin/simple_sidebars/sidebar/widget_add.html', { 'kind': kind, 'form': form, 'sidebar': sidebar, 'widget': widget})

    def delete_sidebar_item(self, request, sidebar_pk, widget_id):
        sidebar = self.check_permissions_for_object(request, Sidebar, sidebar_pk)
        curr = int(widget_id)
        widget = sidebar.get_widget(curr)

        if request.method == "POST":
            post = request.POST.get('post', 'no')
            if post == 'yes':
                version = request.POST['sidebar_version']
                if not sidebar.is_version(version):
                    return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_version_mismatch', args=[sidebar_pk]))
                sidebar.remove_widget(curr)
                sidebar.save()
                return HttpResponseRedirect('../../../')
        else:
            pass
        return render(request, 'admin/simple_sidebars/sidebar/widget_delete.html', {'sidebar': sidebar, 'widget': widget})

    def move_up_item(self, request, sidebar_pk, widget_id):
        sidebar = self.check_permissions_for_object(request, Sidebar, sidebar_pk)
        curr = int(widget_id)
        prev = curr - 1
        widget = sidebar.widgets[curr]
        sidebar.widgets[prev], sidebar.widgets[curr] = sidebar.widgets[curr], sidebar.widgets[prev]
        sidebar.save()
        msg = 'The widget "{0}" was moved successfully.'.format(widget.title)

        messages.success(request, msg)
        return HttpResponseRedirect('../../../')

    def move_down_item(self, request, sidebar_pk, widget_id):
        sidebar = self.check_permissions_for_object(request, Sidebar, sidebar_pk)
        curr = int(widget_id)
        prev = curr + 1
        widget = sidebar.widgets[curr]
        sidebar.widgets[prev], sidebar.widgets[curr] = sidebar.widgets[curr], sidebar.widgets[prev]
        sidebar.save()
        msg = 'The widget "{0}" was moved successfully.'.format(widget.title)

        messages.success(request, msg)
        return HttpResponseRedirect('../../../')

    class Media:
        js = (
            static('admin/simple_sidebars/js/sidebars.js'),
        )
        css = {'all': (static('admin/simple_sidebars/css/sidebars.css'),)}

admin.site.register(Sidebar, SidebarAdmin)
