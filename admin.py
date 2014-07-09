from simple_sidebars.models import Sidebar
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect,Http404, HttpResponse
from django.shortcuts       import render_to_response
from django.template        import RequestContext
from django.core.urlresolvers import reverse
from django.conf.urls import patterns, url
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.utils.encoding import force_unicode

class SidebarAdmin(admin.ModelAdmin):
    exclude = ('widget_schema',)
    readonly_fields = ('version',)
    
    def get_urls(self):
        urls = super(SidebarAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^(?P<sidebar_pk>[-\w]+)/items/add/$', self.admin_site.admin_view(self.add_sidebar_item), name='simple_sidebars_sidebar_additem'),
            url(r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/$', self.admin_site.admin_view(self.edit_sidebar_item), name='simple_sidebars_sidebar_edititem'),
            url(r'^(?P<sidebar_pk>[-\w]+)/version_mismatch/$', self.admin_site.admin_view(self.version_mismatch), name='simple_sidebars_sidebar_version_mismatch'),            
            (r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/delete/$', self.admin_site.admin_view(self.delete_sidebar_item)),
            (r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/move_up/$', self.admin_site.admin_view(self.move_up_item)),
            (r'^(?P<sidebar_pk>[-\w]+)/items/(?P<widget_id>[-\w]+)/move_down/$', self.admin_site.admin_view(self.move_down_item)),
        )
        return my_urls + urls
    
    def get_object_with_change_permissions(self, request, model, obj_pk):
        ''' Helper function that returns a sidebar/sidebaritem if it exists and if the user has the change permissions '''
        try:
            obj = model._default_manager.get(pk=obj_pk)
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None
        if not self.has_change_permission(request, obj):
            raise PermissionDenied
        if obj is None:
            raise Http404('%s object with primary key %r does not exist.' % (model.__name__, escape(obj_pk)))
        return obj
    
    def edit_sidebar_item(self, request, sidebar_pk, widget_id):
        sidebar = self.get_object_with_change_permissions(request, Sidebar, sidebar_pk)        
        widget_id = int(widget_id)        
        widget = sidebar.get_widget(widget_id)
        _WidgetForm = widget.make_form()
        
        if request.method == "POST":
            form = _WidgetForm(request.POST)
            if form.is_valid():
                version = request.POST['sidebar_version']
                if sidebar.is_version(version):
                    widget.update_options(form.cleaned_data)                
                    sidebar.save()
                else:
                    return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_version_mismatch', args=[sidebar_pk]))                    
                return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_change', args=[sidebar_pk]))
        else:
            form = _WidgetForm(widget.get_schema_data())
        kind = widget.widget_kind
        return render_to_response('admin/simple_sidebars/sidebar/widget_add.html', { 'kind':kind, 'form': form, 'sidebar': sidebar, 'widget': widget}, context_instance=RequestContext(request))
    
    def version_mismatch(self, request, sidebar_pk): 
        sidebar = self.get_object_with_change_permissions(request, Sidebar, sidebar_pk)
        return render_to_response('admin/simple_sidebars/sidebar/version_mismatch.html', { 'sidebar': sidebar, }, context_instance=RequestContext(request))
    
    def add_sidebar_item(self, request, sidebar_pk):        
        sidebar = self.get_object_with_change_permissions(request, Sidebar, sidebar_pk)        
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
                if sidebar.is_version(version):
                    widget.update_options(form.cleaned_data)
                    sidebar.add_widget(widget)                
                    sidebar.save()
                else:
                    return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_version_mismatch', args=[sidebar_pk]))
                return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_change', args=[sidebar_pk]))
        else:
            form = _WidgetForm()
            
        return render_to_response('admin/simple_sidebars/sidebar/widget_add.html', { 'kind': kind, 'form': form, 'sidebar': sidebar, 'widget': widget}, context_instance=RequestContext(request))
    
    def delete_sidebar_item(self, request, sidebar_pk, widget_id):
        sidebar = self.get_object_with_change_permissions(request, Sidebar, sidebar_pk)
        curr = int(widget_id)
        widget = sidebar.get_widget(curr)
        
        if request.method == "POST":
            post = request.POST.get('post', 'no')
            if post == 'yes':
                version = request.POST['sidebar_version']
                if sidebar.is_version(version):
                    sidebar.remove_widget(curr)
                    sidebar.save()
                else:
                    return HttpResponseRedirect(reverse('admin:simple_sidebars_sidebar_version_mismatch', args=[sidebar_pk]))
                return HttpResponseRedirect('../../../')
        else:
            pass
        return render_to_response('admin/simple_sidebars/sidebar/widget_delete.html', {'sidebar': sidebar, 'widget': widget}, context_instance=RequestContext(request))
    
    def move_up_item(self, request, sidebar_pk, widget_id):
        sidebar = self.get_object_with_change_permissions(request, Sidebar, sidebar_pk)
        curr = int(widget_id)
        prev = curr - 1
        sidebar.widgets[prev], sidebar.widgets[curr] = sidebar.widgets[curr], sidebar.widgets[prev]
        sidebar.save()
        msg = _('The widget "%s" was moved successfully.') % force_unicode(widget_id)
        
        messages.success(request, msg)
        return HttpResponseRedirect('../../../')
    
    def move_down_item(self, request, sidebar_pk, widget_id):
        sidebar = self.get_object_with_change_permissions(request, Sidebar, sidebar_pk)
        curr = int(widget_id)
        prev = curr + 1
        sidebar.widgets[prev], sidebar.widgets[curr] = sidebar.widgets[curr], sidebar.widgets[prev]
        sidebar.save()
        msg = _('The widget "%s" was moved successfully.') % force_unicode(widget_id)
        
        messages.success(request, msg)
        return HttpResponseRedirect('../../../')
    
    class Media:
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.23/jquery-ui.min.js',
            "/static/js/json2.js",
        )

admin.site.register(Sidebar, SidebarAdmin)
