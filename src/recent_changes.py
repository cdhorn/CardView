# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Jakim Friant
# Copyright (C) 2022  Christopher Horn
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

# $Id$

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from bisect import bisect
from copy import copy

# ------------------------------------------------------------------------
#
# Gtk modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# GRAMPS modules
#
# ------------------------------------------------------------------------
from gramps.gen.plug import Gramplet
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.plug.menu import BooleanOption, NumberOption
from gramps.gui.views.listview import ListView
from gramps.gen.datehandler import format_time
from gramps.gen.utils.callback import Callback
from gramps.gen.utils.db import navigation_label
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
    "Global": _("Global"),
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

# This is dependent on the serialization format of the objects. Unfortunately
# they do not all have POS_ variables for reference. So this is dependent on
# Gramps version, and will break when objects change in the master branch
# during development.

# Index for Gramps 5.1 objects
SERIALIZATION_INDEX = {
    "Person": 17,
    "Family": 12,
    "Event": 10,
    "Place": 15,
    "Source": 8,
    "Citation": 9,
    "Repository": 7,
    "Media": 9,
    "Note": 5,
    "Tag": 4,
}

TAB_OPTION = _("Use tabbed mode")
GLOBAL_OPTION = _("Show global change list")
ALL_OPTION = _("Show all object type lists")
MAX_OBJECTS = _("Maximum objects to display")
ICON_OPTION = _("Use large icons")
ID_OPTION = _("Show Gramps id")


# ------------------------------------------------------------------------
#
# RecentChanges Gramplet
#
# ------------------------------------------------------------------------
class RecentChanges(Gramplet):
    """
    Provides access to history of the most recently modified objects.
    """

    def init(self):
        """
        Set up the GUI
        """
        self.current_view = Gtk.VBox()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.current_view)
        self.change_service = RecentChangesService(self.dbstate)
        self.change_service.connect("change-notification", self.update)
        self.tabbed_mode = 0
        self.show_global_list = 1
        self.show_all_lists = 1
        self.show_gramps_id = 1
        self.large_icons = 0
        self.object_count = 15

    def build_options(self):
        """
        Build the options.
        """
        self.add_option(BooleanOption(TAB_OPTION, bool(self.tabbed_mode)))
        self.add_option(
            BooleanOption(GLOBAL_OPTION, bool(self.show_global_list))
        )
        self.add_option(BooleanOption(ALL_OPTION, bool(self.show_all_lists)))
        self.add_option(NumberOption(MAX_OBJECTS, self.object_count, 1, 25))
        self.add_option(BooleanOption(ICON_OPTION, bool(self.large_icons)))
        self.add_option(BooleanOption(ID_OPTION, bool(self.show_gramps_id)))

    def save_options(self):
        """
        Save the options.
        """
        self.tabbed_mode = int(self.get_option(TAB_OPTION).get_value())
        self.show_global_list = int(self.get_option(GLOBAL_OPTION).get_value())
        self.show_all_lists = int(self.get_option(ALL_OPTION).get_value())
        self.object_count = int(self.get_option(MAX_OBJECTS).get_value())
        self.large_icons = int(self.get_option(ICON_OPTION).get_value())
        self.show_gramps_id = int(self.get_option(ID_OPTION).get_value())

    def on_load(self):
        """
        Load the options.
        """
        if len(self.gui.data) == 6:
            self.tabbed_mode = int(self.gui.data[0])
            self.show_global_list = int(self.gui.data[1])
            self.show_all_lists = int(self.gui.data[2])
            self.object_count = int(self.gui.data[3])
            self.large_icons = int(self.gui.data[4])
            self.show_gramps_id = int(self.gui.data[5])

    def save_update_options(self, widget=None):
        """
        Save updated options.
        """
        self.tabbed_mode = int(self.get_option(TAB_OPTION).get_value())
        self.show_global_list = int(self.get_option(GLOBAL_OPTION).get_value())
        self.show_all_lists = int(self.get_option(ALL_OPTION).get_value())
        self.object_count = int(self.get_option(MAX_OBJECTS).get_value())
        self.large_icons = int(self.get_option(ICON_OPTION).get_value())
        self.show_gramps_id = int(self.get_option(ID_OPTION).get_value())
        self.gui.data = [
            self.tabbed_mode,
            self.show_global_list,
            self.show_all_lists,
            self.object_count,
            self.large_icons,
            self.show_gramps_id,
        ]
        self.update()

    def main(self):
        """
        Fetch record change history and render.
        """
        self.change_history = self.change_service.get_change_history()
        nav_type = self.uistate.viewmanager.active_page.navigation_type()
        list(map(self.current_view.remove, self.current_view.get_children()))

        if self.show_all_lists:
            display_list_types = [x for x in CATEGORIES]
        else:
            display_list_types = [nav_type]
        if not self.show_global_list:
            display_list_types.remove("Global")

        if self.tabbed_mode:
            self.render_tabbed_mode(nav_type, display_list_types)
        else:
            self.render_expander_mode(nav_type, display_list_types)
        self.current_view.show_all()

    def build_list(self, nav_type, handle_list, current=False):
        """
        Build history widget list for an object type.
        """
        list_widget = Gtk.VBox(vexpand=False)
        for obj_type, obj_handle, label, _change, change_string in handle_list[
            : self.object_count
        ]:
            if self.show_gramps_id:
                title = label
            else:
                title = label.split("]")[1].strip()
            model = RecentChangesModel(
                self.dbstate,
                obj_type,
                obj_handle,
                title,
                change_string,
                self.large_icons,
            )
            view = RecentChangesView(self.uistate)
            RecentChangesPresenter(model, view)
            list_widget.pack_start(view, False, False, 0)
        return list_widget

    def render_expander_mode(self, nav_type, display_list_types):
        """
        Render using the expander more.
        """
        for list_type in display_list_types:
            current_type = list_type == nav_type
            list_widget = self.build_list(
                list_type, self.change_history[list_type], current_type
            )
            list_expander = Gtk.Expander(expanded=current_type)
            list_expander.set_label(CATEGORIES_LANG[list_type])
            list_expander.add(list_widget)
            self.current_view.pack_start(list_expander, False, False, 0)

    def render_tabbed_mode(self, nav_type, display_list_types):
        """
        Render using the tabbed mode.
        """
        notebook = Gtk.Notebook(vexpand=True, hexpand=True)
        tab_count = 0
        current_page = 0
        for list_type in display_list_types:
            current_type = list_type == nav_type
            if current_type:
                current_page = tab_count
            tab_widget = self.build_list(
                list_type, self.change_history[list_type], current_type
            )
            tab_icon = self.get_tab_icon(list_type)
            notebook.append_page(tab_widget, tab_icon)
            tab_count = tab_count + 1
        notebook.set_current_page(current_page)
        css = ".notebook tab { border: 0px; margin: 0px; }".encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = notebook.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("notebook")
        vbox = Gtk.VBox(vexpand=False)
        vbox.pack_start(notebook, False, False, 0)
        self.current_view.pack_start(vbox, False, False, 0)

    def get_tab_icon(self, list_type):
        """
        Get proper tab icon to use.
        """
        if list_type == "Global":
            icon_name = "gramps-gramplet"
        elif list_type == "Note":
            icon_name = "gramps-notes"
        else:
            icon_name = "gramps-{}".format(list_type.lower())
        icon = Gtk.Image()
        if self.large_icons:
            icon.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        else:
            icon.set_from_icon_name(icon_name, Gtk.IconSize.SMALL_TOOLBAR)
        return icon


# ------------------------------------------------------------------------
#
# RecentChangesService class
#
# The general idea here is that if different views or gramplets are going to
# make use of this data we should only collect and update it a single time
# in one place and let them reference it there as needed.
#
# ------------------------------------------------------------------------
class RecentChangesService(Callback):
    """
    A singleton for centrally tracking changed objects in the database.
    """

    __signals__ = {"change-notification": (str, str)}

    __slots__ = ("dbstate", "depth", "change_history", "signal_map")

    __init = False

    def __new__(cls, *args, **kwargs):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(RecentChangesService, cls).__new__(cls)
        return cls.instance

    def __init__(self, dbstate, depth=25):
        """
        Initialize the class if needed.
        """
        if not self.__init:
            Callback.__init__(self)
            self.dbstate = dbstate
            self.depth = depth
            self.change_history = {}
            self.signal_map = {}

            self.register_signal("Person")
            self.register_signal("Family")
            self.register_signal("Event")
            self.register_signal("Place")
            self.register_signal("Source")
            self.register_signal("Citation")
            self.register_signal("Repository")
            self.register_signal("Media")
            self.register_signal("Note")
            self.register_signal("Tag")
            self.initialize_change_history()
            dbstate.connect("database-changed", self.initialize_change_history)
            self.__init = True

    def register_signal(self, object_type):
        """
        Register signal.
        """
        update_function = lambda x: self.update_change_history(x, object_type)
        delete_function = lambda x: self.delete_change_history(x, object_type)
        lower_type = object_type.lower()
        for sig in ["add", "update", "rebuild"]:
            self.signal_map["{}-{}".format(lower_type, sig)] = update_function
        self.signal_map["{}-delete".format(lower_type)] = delete_function

    def change_depth(self, depth):
        """
        Change depth, rebuild list and issue synthetic change notification.
        """
        self.depth = depth
        self.load_change_history()
        if self.change_history["Global"]:
            last_object = self.change_history["Global"][0]
            self.emit("change-notification", (last_object[0], last_object[1]))

    def load_change_history(self):
        """
        Load the change history.
        """
        self.change_history = get_all_object_handles(
            self.dbstate.db, self.depth
        )

    def initialize_change_history(self, *args):
        """
        Rebuild history and connect database signals for change notifications.
        """
        self.load_change_history()
        for sig, callback in self.signal_map.items():
            self.dbstate.db.connect(sig, callback)

    def update_change_history(self, object_handles, object_type):
        """
        Update history and emit object modification signal.
        """
        if object_handles:
            object_handle = object_handles[0]
            self.clean_change_history(object_type, object_handle)
            object_label, changed_object = get_object_label(
                self.dbstate.db, object_type, object_handle
            )
            changed_tuple = (
                object_type,
                object_handle,
                object_label,
                changed_object.change,
                format_time(changed_object.change),
            )
            self.change_history[object_type].insert(0, changed_tuple)
            if len(self.change_history[object_type]) > self.depth:
                self.change_history[object_type].pop()
            self.change_history["Global"].insert(0, changed_tuple)
            if len(self.change_history["Global"]) > self.depth:
                self.change_history["Global"].pop()
            self.emit("change-notification", (object_type, object_handle))

    def clean_change_history(self, object_type, object_handle):
        """
        Remove the given object from the history if it is present.
        """
        for index in ["Global", object_type]:
            for object_data in self.change_history[index]:
                if object_data[1] == object_handle:
                    self.change_history[index].remove(object_data)

    def delete_change_history(self, object_handles, object_type):
        """
        If deleted from history rebuild history and emit notification.
        """
        if object_handles:
            object_handle = object_handles[0]
            if self.check_removed_object(
                object_type, object_handle
            ) or self.check_removed_object("Global", object_handle):
                self.load_change_history()
                self.emit("change-notification", (object_type, object_handle))

    def check_removed_object(self, object_type, object_handle):
        """
        Check if deleted handle in current history.
        """
        for object_data in self.change_history[object_type]:
            if object_data[1] == object_handle:
                return True
        return False

    def get_change_history(self, obj_type=None):
        """
        Return change history.
        """
        if obj_type in self.change_history:
            return self.change_history[obj_type]
        return self.change_history


# ------------------------------------------------------------------------
#
# RecentChangesModel class
#
# ------------------------------------------------------------------------
class RecentChangesModel:
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
        "size",
    )

    def __init__(self, dbstate, obj_type, obj_handle, title, text, size=0):
        self.dbstate = dbstate
        self.obj_type = obj_type
        self.obj_handle = obj_handle
        self.title = title
        self.text = text
        if obj_type == "Note":
            self.icon = "gramps-notes"
        else:
            self.icon = "gramps-{}".format(obj_type.lower())
        self.size = size

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
# RecentChangesInteractor class
#
# ------------------------------------------------------------------------
class RecentChangesInteractor:
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
        if action == "left":
            return self.presenter.goto()


# ------------------------------------------------------------------------
#
# RecentChangesPresenter class
#
# ------------------------------------------------------------------------
class RecentChangesPresenter:
    """
    Update the view based on the model.
    """

    __slots__ = "model", "view"

    def __init__(self, model, view):
        self.model = model
        self.view = view
        RecentChangesInteractor(self, view)
        self.load_view()

    def load_view(self):
        """
        Load the data into the view.
        """
        self.view.set_title(self.model.title)
        self.view.set_text(self.model.text)
        self.view.set_icon(self.model.icon, size=self.model.size)

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

    def goto(self):
        """
        Perform a requested navigation action.
        """
        category = CATEGORIES[self.model.obj_type]
        category_index = self.view.uistate.viewmanager.get_category(category)
        self.view.uistate.viewmanager.goto_page(category_index, None)
        history = self.view.uistate.get_history(self.model.obj_type)
        if history:
            history.push(self.model.obj_handle)
        return True


# ------------------------------------------------------------------------
#
# RecentChangesView class
#
# ------------------------------------------------------------------------
class RecentChangesView(Gtk.Bin):
    """
    Render the graphical view.
    """

    __slots__ = "uistate", "callback", "widgets"

    def __init__(self, uistate):
        Gtk.Bin.__init__(self)
        self.uistate = uistate
        self.callback = None
        self.widgets = RecentChangesWidgets()
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

    def enter(self, *args):
        """
        Indicate focus when cursor enters widget.
        """
        self.set_css(2)

    def leave(self, *args):
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

    def clicked(self, obj, event):
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
                name, Gtk.IconSize.LARGE_TOOLBAR
            )
        else:
            self.widgets.icon.set_from_icon_name(
                name, Gtk.IconSize.SMALL_TOOLBAR
            )


# ------------------------------------------------------------------------
#
# RecentChangesWidgets class
#
# ------------------------------------------------------------------------
class RecentChangesWidgets:
    """
    Encapsulate the view widgets.
    """

    __slots__ = "frame", "events", "title", "text", "icon"

    def __init__(self):
        self.frame = Gtk.Frame()
        self.events = Gtk.EventBox()
        self.title = Gtk.Label(xalign=0.0)
        self.text = Gtk.Label(xalign=0.0)
        self.icon = Gtk.Image()


# ------------------------------------------------------------------------
#
# KeyWrapper class
#
# ------------------------------------------------------------------------
class KeyWrapper:
    """
    For bisect to operate on an element of a tuple in the list.
    """

    __slots__ = "iter", "key"

    def __init__(self, iterable, key):
        self.iter = iterable
        self.key = key

    def __getitem__(self, i):
        return self.key(self.iter[i])

    def __len__(self):
        return len(self.iter)


# ------------------------------------------------------------------------
#
# Utility functions
#
# ------------------------------------------------------------------------
def get_object_label(db, object_type, object_handle):
    """
    Generate meaningful label for the object.
    """
    if object_type != "Tag":
        name, obj = navigation_label(db, object_type, object_handle)
    else:
        obj = db.get_tag_from_handle(object_handle)
        name = "".join(("[", _("Tag"), "] ", obj.get_name()))
    return name, obj


def get_formatted_handle_list(db, handle_list):
    """
    Prepare a label and formatted time for all the objects.
    """
    full_list = []
    for (object_type, object_handle, change) in handle_list:
        change = -change
        label, dummy_obj = get_object_label(db, object_type, object_handle)
        full_list.append(
            (object_type, object_handle, label, change, format_time(change))
        )
    return full_list


def get_latest_handles(db, object_type, list_method, depth=10):
    """
    Get the most recently changed object handles for a given object type.
    """
    handle_list = []
    raw_method = db.method("get_raw_%s_data", object_type.lower())
    change_index = SERIALIZATION_INDEX[object_type]
    for object_handle in list_method():
        change = -raw_method(object_handle)[change_index]
        bsindex = bisect(KeyWrapper(handle_list, key=lambda c: c[2]), change)
        handle_list.insert(bsindex, (object_type, object_handle, change))
        if len(handle_list) > depth:
            handle_list.pop(depth)
    return get_formatted_handle_list(db, handle_list)


def get_all_object_handles(db, depth=10):
    """
    Gather and return all recently changed handles and a coalesced global list.
    """
    change_history = {}
    global_history = []
    for object_type in SERIALIZATION_INDEX:
        if object_type == "Citation":
            list_method = db.get_citation_handles
        else:
            list_method = db.method("iter_%s_handles", object_type.lower())
        handle_list = get_latest_handles(db, object_type, list_method, depth)
        change_history[object_type] = handle_list
        global_history = global_history + handle_list
    global_history.sort(key=lambda x: x[3], reverse=True)
    change_history["Global"] = global_history[:depth]
    return change_history
