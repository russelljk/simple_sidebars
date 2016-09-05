from django.test import TestCase
from simple_sidebars import widgets
from simple_sidebars.models import *


class TestWidgetRequired(widgets.Widget):
    widget_kind = "test_widget_required"
    required_char_field = widgets.CharOption(required=True)


class TestWidgetOptional(widgets.Widget):
    widget_kind = "test_widget_optional"
    optional_char_field = widgets.CharOption(required=False, default="Testing")


class TestWidgetSample(widgets.Widget):
    widget_kind = "test_widget_sample"
    test_value = widgets.IntegerOption(required=False, default=0)


class SidebarTestCase(TestCase):
    def setUp(self):
        self.sidebar = Sidebar(title="Test Sidebar")
        self.sidebar.save()


class SidebarTests(SidebarTestCase):
    pass


class WidgetTests(SidebarTestCase):
    def test_add_widget(self):
        for i in range(5):
            widget = TestWidgetSample({}, add=True)
            widget.update_options({"title": "Sample Widget {0}".format(i)})

            self.sidebar.add_widget(widget)
            self.sidebar.save()
            self.sidebar.refresh_from_db()
            self.assertEquals(len(self.sidebar.widgets), i + 1, "Test that widget was added")

    def setupWidgets(self):
        for i in range(5):
            widget = TestWidgetSample({}, add=True)
            widget.update_options({"title": "Sample Widget {0}".format(i), "test_value": i})

            self.sidebar.add_widget(widget)
            self.sidebar.save()
        self.sidebar.refresh_from_db()

    def test_delete_widget(self):
        self.setupWidgets()

        self.sidebar.remove_widget(0)
        self.sidebar.save()
        self.sidebar.refresh_from_db()

        self.assertEquals(len(self.sidebar.widgets), 4, "Test that widget was removed.")
        self.assertEquals(self.sidebar.widgets[0].test_value, 1, "Test that widget the correct widget was removed.")

        self.sidebar.remove_widget(2)
        self.sidebar.save()
        self.sidebar.refresh_from_db()
        self.assertEquals(len(self.sidebar.widgets), 3, "Test that widget was removed.")
        self.assertEquals(self.sidebar.widgets[2].test_value, 4, "Test that widget the correct widget was removed.")
        self.assertEquals(self.sidebar.widgets[1].test_value, 2, "Test that widget the correct widget was removed.")

    def test_move_widget_up(self):
        self.setupWidgets()

    def test_move_widget_down(self):
        self.setupWidgets()


class TestWidgetOptions(SidebarTestCase):
    def test_required_options(self):
        pass
