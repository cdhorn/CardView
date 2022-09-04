#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022  Christopher Horn
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
ChangesObjectView
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from html import escape

# ------------------------------------------------------------------------
#
# Gtk modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import (
    EditCitation,
    EditEvent,
    EditFamily,
    EditMedia,
    EditNote,
    EditPerson,
    EditPlace,
    EditRepository,
    EditSource,
)
from gramps.gui.views.tags import EditTag

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .view_base import GrampsObjectView
from ..services.service_statistics import StatisticsService

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

# The key sequence here is used for the group rendering order
CATEGORIES = {
    "Global": "Global",
    "Person": "People",
    "Family": "Families",
    "Event": "Events",
    "Place": "Places",
    "Source": "Sources",
    "Citation": "Citations",
    "Repository": "Repositories",
    "Media": "Media",
    "Note": "Notes",
    "Tag": "Tags",
}

CATEGORIES_LANG = {
    "Global": _("All objects"),
    "Person": _("People"),
    "Family": _("Families"),
    "Event": _("Events"),
    "Place": _("Places"),
    "Source": _("Sources"),
    "Citation": _("Citations"),
    "Repository": _("Repositories"),
    "Media": _("Media"),
    "Note": _("Notes"),
    "Tag": _("Tags"),
}

EDITORS = {
    "Person": EditPerson,
    "Family": EditFamily,
    "Event": EditEvent,
    "Place": EditPlace,
    "Source": EditSource,
    "Citation": EditCitation,
    "Repository": EditRepository,
    "Media": EditMedia,
    "Note": EditNote,
    "Tag": EditTag,
}


# -------------------------------------------------------------------------
#
# ChangesView Class
#
# -------------------------------------------------------------------------
class ChangesObjectView(GrampsObjectView):
    """
    Provides the changes view.
    """

    def __init__(self, grstate, grcontext):
        GrampsObjectView.__init__(self, grstate, grcontext)
        self.change_service = StatisticsService(grstate)
        self.change_service.connect("changes-updated", self.load_data)
        self.change_history = {}
        self.stack = None
        self.stack_state = None
        self.stack_active_button = None
        self.max_per_list = 20
        self.load_data()

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        self.view_body = Gtk.Box()

    def load_data(self, *_dummy_args):
        """
        Fetch record change history and render.
        """
        if self.stack:
            self.stack_state = self.stack.get_visible_child_name()

        self.change_history = self.change_service.get_change_history()

        list(map(self.view_body.remove, self.view_body.get_children()))
        if self.grstate.dbstate.is_open():
            nav_type = "Global"
            self.render_stacked_mode(nav_type, CATEGORIES)
        self.view_body.show_all()

    def build_list(self, handle_list):
        """
        Build history widget list for an object type.
        """
        list_widget = Gtk.VBox(vexpand=False, hexpand=True)
        for (
            obj_type,
            obj_handle,
            label,
            dummy_change,
            change_string,
        ) in handle_list[: self.max_per_list]:
            model = LastChangedModel(
                self.grstate.dbstate,
                obj_type,
                obj_handle,
                escape(label),
                "<small>{}</small>".format(change_string),
            )
            view = LastChangedView(self.grstate.uistate)
            LastChangedPresenter(model, view)
            list_widget.pack_start(view, True, True, 0)
        return list_widget

    def render_stacked_mode(self, nav_type, display_list_types):
        """
        Render using the stacked mode.
        """
        grid = Gtk.Grid()
        button_list = Gtk.HBox(spacing=0, margin=0)
        grid.attach(button_list, 0, 0, 1, 1)
        self.stack = Gtk.Stack(vexpand=False)
        grid.attach(self.stack, 0, 1, 1, 1)
        set_relief = False
        current_button = None
        for list_type in display_list_types:
            current_type = list_type == nav_type
            if list_type in self.change_history:
                list_history = self.change_history[list_type]
            else:
                list_history = []
            stack_widget = self.build_list(list_history)
            self.stack.add_named(stack_widget, list_type)
            stack_button = self.get_stack_button(list_type)
            if self.stack_state and self.stack_state == list_type:
                self.stack_active_button = stack_button
                set_relief = True
            if current_type:
                current_button = stack_button
            button_list.pack_start(stack_button, False, False, 0)
        if not set_relief and current_button:
            self.stack_active_button = current_button
        self.stack_active_button.set_relief(Gtk.ReliefStyle.NORMAL)
        self.stack.show_all()
        if self.stack_state:
            self.stack.set_visible_child_name(self.stack_state)
        else:
            self.stack.set_visible_child_name(nav_type)
        self.view_body.pack_start(grid, True, True, 0)

    def switch_stack(self, button, name):
        """
        Switch to new stack page.
        """
        if self.stack_active_button:
            self.stack_active_button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_relief(Gtk.ReliefStyle.NORMAL)
        self.stack_active_button = button
        self.stack.set_visible_child_name(name)

    def get_stack_button(self, list_type):
        """
        Get proper stack button with icon to use.
        """
        if list_type == "Global":
            icon_name = "gramps-gramplet"
        elif list_type == "Note":
            icon_name = "gramps-notes"
        else:
            icon_name = "gramps-{}".format(list_type.lower())
        icon = Gtk.Image()
        icon.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        button = Gtk.Button(relief=Gtk.ReliefStyle.NONE)
        button.set_image(icon)
        button.connect("clicked", self.switch_stack, list_type)
        button.connect("enter-notify-event", self.enter_stack_button)
        button.connect("leave-notify-event", self.leave_stack_button)
        button.set_tooltip_text(CATEGORIES_LANG[list_type])
        return button

    def enter_stack_button(self, widget, _dummy_event):
        """
        Indicate focus when cursor enters widget.
        """
        widget.set_relief(Gtk.ReliefStyle.NORMAL)

    def leave_stack_button(self, widget, _dummy_event):
        """
        Clear focus when cursor leaves widget.
        """
        if self.stack_active_button != widget:
            widget.set_relief(Gtk.ReliefStyle.NONE)


# ------------------------------------------------------------------------
#
# LastChangedModel class
#
# ------------------------------------------------------------------------
class LastChangedModel:
    """
    Model for presentation layer.
    """

    __slots__ = (
        "dbstate",
        "obj_type",
        "obj_handle",
        "title",
        "text",
        "icon",
    )

    def __init__(self, dbstate, obj_type, obj_handle, title, text):
        self.dbstate = dbstate
        self.obj_type = obj_type
        self.obj_handle = obj_handle
        self.title = title
        self.text = text
        if obj_type == "Note":
            self.icon = "gramps-notes"
        else:
            self.icon = "gramps-{}".format(obj_type.lower())

    def get_object(self):
        """
        Fetch and return the object.
        """
        query = self.dbstate.db.method(
            "get_%s_from_handle", self.obj_type.lower()
        )
        return query(self.obj_handle)


# ------------------------------------------------------------------------
#
# LastChangedInteractor class
#
# ------------------------------------------------------------------------
class LastChangedInteractor:
    """
    Interaction handler for presentation layer.
    """

    __slots__ = "presenter", "view"

    def __init__(self, presenter, view):
        self.presenter = presenter
        self.view = view
        view.connect(self.handler)

    def handler(self, action):
        """
        Call presenter to perform requested action.
        """
        if action == "right":
            return self.presenter.edit()
        if action == "middle":
            return self.presenter.goto_list_view()
        if action == "left":
            return self.presenter.goto_card_view()


# ------------------------------------------------------------------------
#
# LastChangedPresenter class
#
# ------------------------------------------------------------------------
class LastChangedPresenter:
    """
    Update the view based on the model.
    """

    __slots__ = "model", "view"

    def __init__(self, model, view):
        self.model = model
        self.view = view
        LastChangedInteractor(self, view)
        self.load_view()

    def load_view(self):
        """
        Load the data into the view.
        """
        self.view.set_title(self.model.title)
        self.view.set_text(self.model.text)
        self.view.set_icon(self.model.icon)

    def edit(self):
        """
        Perform a requested edit action.
        """
        if self.model.obj_type in EDITORS:
            editor = EDITORS[self.model.obj_type]
            if editor:
                try:
                    editor(
                        self.model.dbstate,
                        self.view.uistate,
                        [],
                        self.model.get_object(),
                    )
                except WindowActiveError:
                    pass
        return True

    def goto_list_view(self):
        """
        Navigate to a list view.
        """
        self.goto(list_view=True)

    def goto_card_view(self):
        """
        Navigate to a card view.
        """
        self.goto(list_view=False)

    def goto(self, list_view=False):
        """
        Perform a requested navigation action.
        """
        viewmanager = self.view.uistate.viewmanager
        category = CATEGORIES[self.model.obj_type]
        category_index = viewmanager.get_category(category)
        if list_view:
            viewmanager.goto_page(category_index, 0)
        else:
            found = False
            category_views = viewmanager.get_views()[category_index]
            if category_views:
                for (view_index, (view_plugin, dummy_view_class)) in enumerate(
                    category_views
                ):
                    if "cardview" in view_plugin.id:
                        viewmanager.goto_page(category_index, view_index)
                        found = True
                        break
            if not found:
                viewmanager.goto_page(category_index, None)

        nav_group = self.view.uistate.viewmanager.active_page.nav_group
        if nav_group == 1:
            history = self.view.uistate.get_history("Global", nav_group)
            if history:
                self.view.uistate.viewmanager.active_page.dirty = 1
                history.push((self.model.obj_type, self.model.obj_handle))
                return True
        history = self.view.uistate.get_history(self.model.obj_type)
        history.push(self.model.obj_handle)
        return True


# ------------------------------------------------------------------------
#
# LastChangedView class
#
# ------------------------------------------------------------------------
class LastChangedView(Gtk.Bin):
    """
    Render the graphical view.
    """

    __slots__ = "uistate", "callback", "widgets"

    def __init__(self, uistate):
        Gtk.Bin.__init__(self)
        self.uistate = uistate
        self.callback = None
        self.widgets = LastChangedWidgets()
        self.__build_layout(self.widgets)
        self.widgets.events.connect("button-press-event", self.clicked)
        self.widgets.events.connect("enter-notify-event", self.enter)
        self.widgets.events.connect("leave-notify-event", self.leave)
        self.show()

    def __build_layout(self, widgets):
        """
        Build the widget layout.
        """
        self.add(widgets.events)
        widgets.events.add(widgets.frame)
        hbox = Gtk.HBox()
        hbox.pack_start(widgets.icon, False, False, 6)
        vbox = Gtk.VBox()
        hbox.pack_start(vbox, False, False, 0)
        vbox.pack_start(widgets.title, True, True, 0)
        vbox.pack_start(widgets.text, True, True, 0)
        widgets.frame.add(hbox)
        self.set_css(1)

    def enter(self, *_dummy_args):
        """
        Indicate focus when cursor enters widget.
        """
        self.set_css(2)

    def leave(self, *_dummy_args):
        """
        Clear focus when cursor leaves widget.
        """
        self.set_css(1)

    def set_css(self, border):
        """
        Adjust the frame styling.
        """
        css = "".join(
            (
                ".frame { border: solid; border-radius: 5px; border-width: ",
                str(border),
                "px; }",
            )
        ).encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = self.widgets.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")

    def connect(self, callback):
        """
        Connect a callback for the interactor.
        """
        self.callback = callback

    def clicked(self, _dummmy_obj, event):
        """
        Handle calling interactor for a click event.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS:
            action = None
            if event.button == Gdk.BUTTON_PRIMARY:
                action = "left"
            elif event.button == Gdk.BUTTON_MIDDLE:
                action = "middle"
            elif event.button == Gdk.BUTTON_SECONDARY:
                action = "right"
            if action and self.callback:
                self.callback(action)

    def set_title(self, title):
        """
        Set the title.
        """
        self.widgets.title.set_label(title)

    def set_text(self, text):
        """
        Set the additional text field.
        """
        self.widgets.text.set_label(text)

    def set_icon(self, name, size=0):
        """
        Set the icon.
        """
        if size:
            self.widgets.icon.set_from_icon_name(
                name, Gtk.IconSize.SMALL_TOOLBAR
            )
        else:
            self.widgets.icon.set_from_icon_name(
                name, Gtk.IconSize.LARGE_TOOLBAR
            )


# ------------------------------------------------------------------------
#
# LastChangedWidgets class
#
# ------------------------------------------------------------------------
class LastChangedWidgets:
    """
    Encapsulate the view widgets.
    """

    __slots__ = "frame", "events", "title", "text", "icon"

    def __init__(self):
        self.frame = Gtk.Frame()
        self.events = Gtk.EventBox()
        self.title = Gtk.Label(xalign=0.0, use_markup=True)
        self.text = Gtk.Label(xalign=0.0, use_markup=True)
        self.icon = Gtk.Image()
