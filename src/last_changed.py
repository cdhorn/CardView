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
from html import escape
from threading import Lock

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

YIELD_COUNT = 2000

MAXIMUM_OBJECTS = _("Maximum objects to display")
ENABLE_SMALL_ICONS = _("Use small icons")
ENABLE_SMALL_TEXT = _("Use smaller text for change time")
ENABLE_GRAMPS_ID = _("Include Gramps id")
ENABLE_OVERVIEW = _("Enable overview")
ENABLE_PEOPLE = _("Enable people")
ENABLE_FAMILIES = _("Enable families")
ENABLE_EVENTS = _("Enable events")
ENABLE_PLACES = _("Enable places")
ENABLE_SOURCES = _("Enable sources")
ENABLE_CITATIONS = _("Enable citations")
ENABLE_REPOSITORIES = _("Enable repositories")
ENABLE_MEDIA = _("Enable media")
ENABLE_NOTES = _("Enable notes")
ENABLE_TAGS = _("Enable tags")

# ------------------------------------------------------------------------
#
# LastChanged Gramplet
#
# ------------------------------------------------------------------------
class LastChanged(Gramplet):
    """
    Provides access to history of the most recently modified objects.
    """

    def init(self):
        """
        Set up the GUI
        """
        self.current_view = Gtk.VBox(vexpand=True)
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.current_view)
        self.change_service = LastChangedService(self.dbstate, self.uistate)
        self.change_service.connect("change-notification", self.update)
        self.change_history = {}
        self.stack = None
        self.stack_state = None
        self.stack_active_button = None
        self.max_per_list = 10
        self.enable_small_icons = 0
        self.enable_small_text = 1
        self.enable_gramps_id = 1

    def build_options(self):
        """
        Build the options.
        """
        self.add_option(
            NumberOption(MAXIMUM_OBJECTS, self.max_per_list, 1, 25)
        )
        self.add_option(
            BooleanOption(ENABLE_SMALL_ICONS, bool(self.enable_small_icons))
        )
        self.add_option(
            BooleanOption(ENABLE_SMALL_TEXT, bool(self.enable_small_text))
        )
        self.add_option(
            BooleanOption(ENABLE_GRAMPS_ID, bool(self.enable_gramps_id))
        )

    def save_options(self):
        """
        Save the options.
        """
        self.max_per_list = int(self.get_option(MAXIMUM_OBJECTS).get_value())
        self.enable_small_icons = int(
            self.get_option(ENABLE_SMALL_ICONS).get_value()
        )
        self.enable_small_text = int(
            self.get_option(ENABLE_SMALL_TEXT).get_value()
        )
        self.enable_gramps_id = int(
            self.get_option(ENABLE_GRAMPS_ID).get_value()
        )

    def on_load(self):
        """
        Load the options.
        """
        if len(self.gui.data) == 4:
            self.max_per_list = int(self.gui.data[0])
            self.enable_small_icons = int(self.gui.data[1])
            self.enable_small_text = int(self.gui.data[2])
            self.enable_gramps_id = int(self.gui.data[3])

    def save_update_options(self, widget=None):
        """
        Save updated options.
        """
        self.save_options()
        self.gui.data = [
            self.max_per_list,
            self.enable_small_icons,
            self.enable_small_text,
            self.enable_gramps_id,
        ]
        self.update()

    def main(self):
        """
        Fetch record change history and render.
        """
        if self.stack:
            self.stack_state = self.stack.get_visible_child_name()

        if self.dbstate.is_open():
            with self.change_service.history_lock:
                self.change_history = self.change_service.get_change_history()
        if self.change_history == {} and self.dbstate.is_open():
            list(
                map(self.current_view.remove, self.current_view.get_children())
            )
            label = Gtk.Label(
                xalign=0.0, use_markup=True, label=_("Processing history...")
            )
            self.current_view.pack_start(label, False, False, 0)
            self.current_view.show_all()
            counter = 0
            db = self.dbstate.db
            self.change_history = {}
            global_history = []
            for object_type in SERIALIZATION_INDEX:
                self.update_label(label, object_type)
                if object_type == "Citation":
                    list_method = db.get_citation_handles
                else:
                    list_method = db.method(
                        "iter_%s_handles", object_type.lower()
                    )

                handle_list = []
                raw_method = db.method("get_raw_%s_data", object_type.lower())
                change_index = SERIALIZATION_INDEX[object_type]
                for object_handle in list_method():
                    change = -raw_method(object_handle)[change_index]
                    bsindex = bisect(
                        KeyWrapper(handle_list, key=lambda c: c[2]), change
                    )
                    handle_list.insert(
                        bsindex, (object_type, object_handle, change)
                    )
                    if len(handle_list) > self.max_per_list:
                        handle_list.pop(self.max_per_list)
                    if counter % YIELD_COUNT:
                        yield True
                    counter += 1
                formatted_history = get_formatted_handle_list(db, handle_list)
                self.change_history[object_type] = formatted_history
                global_history = global_history + formatted_history
            global_history.sort(key=lambda x: x[3], reverse=True)
            self.change_history["Global"] = global_history[: self.max_per_list]
            self.change_service.history_lock.acquire()
            self.change_service.set_change_history(self.change_history)
            self.change_service.history_lock.release()

        list(map(self.current_view.remove, self.current_view.get_children()))
        if self.dbstate.is_open() and self.uistate.viewmanager.active_page:
            nav_type = self.uistate.viewmanager.active_page.navigation_type()
            if not nav_type:
                nav_type = "Global"
            self.render_stacked_mode(nav_type, CATEGORIES)
        self.current_view.show_all()
        yield False

    def update_label(self, label, obj_type):
        """
        Update label.
        """
        TOTALS = {
            "Person": self.dbstate.db.get_number_of_people,
            "Family": self.dbstate.db.get_number_of_families,
            "Event": self.dbstate.db.get_number_of_events,
            "Place": self.dbstate.db.get_number_of_places,
            "Source": self.dbstate.db.get_number_of_sources,
            "Citation": self.dbstate.db.get_number_of_citations,
            "Repository": self.dbstate.db.get_number_of_repositories,
            "Media": self.dbstate.db.get_number_of_media,
            "Note": self.dbstate.db.get_number_of_notes,
            "Tag": self.dbstate.db.get_number_of_tags,
        }
        total = TOTALS[obj_type]()

        text = "{} {} {}...".format(
            _("Evaluating"), total, CATEGORIES_LANG[obj_type]
        )
        label.set_text(text)

    def build_list(self, nav_type, handle_list, current=False):
        """
        Build history widget list for an object type.
        """
        list_widget = Gtk.VBox(vexpand=False)
        for obj_type, obj_handle, label, _change, change_string in handle_list[
            : self.max_per_list
        ]:
            if self.enable_small_text:
                change_string = "<small>{}</small>".format(change_string)
            if self.enable_gramps_id:
                title = escape(label)
            else:
                title = escape(label.split("]")[1].strip())
            model = LastChangedModel(
                self.dbstate,
                obj_type,
                obj_handle,
                title,
                change_string,
                self.enable_small_icons,
            )
            view = LastChangedView(self.uistate)
            LastChangedPresenter(model, view)
            list_widget.pack_start(view, False, False, 0)
        return list_widget

    def render_stacked_mode(self, nav_type, display_list_types):
        """
        Render using the stacked mode.
        """
        grid = Gtk.Grid()
        button_list = Gtk.HBox(hexpand=False, spacing=0, margin=0)
        grid.attach(button_list, 0, 0, 1, 1)
        self.stack = Gtk.Stack(vexpand=True, hexpand=True)
        grid.attach(self.stack, 0, 1, 1, 1)
        set_relief = False
        current_button = None
        for list_type in display_list_types:
            current_type = list_type == nav_type
            stack_widget = self.build_list(
                list_type, self.change_history[list_type], current_type
            )
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
        vbox = Gtk.VBox(vexpand=False)
        vbox.pack_start(grid, False, False, 0)
        self.current_view.pack_start(vbox, False, False, 0)

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
        if self.enable_small_icons:
            icon.set_from_icon_name(icon_name, Gtk.IconSize.SMALL_TOOLBAR)
        else:
            icon.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        button = Gtk.Button(relief=Gtk.ReliefStyle.NONE)
        button.set_image(icon)
        button.connect("clicked", self.switch_stack, list_type)
        button.connect("enter-notify-event", self.enter_stack_button)
        button.connect("leave-notify-event", self.leave_stack_button)
        button.set_tooltip_text(CATEGORIES_LANG[list_type])
        return button

    def enter_stack_button(self, widget, event):
        """
        Indicate focus when cursor enters widget.
        """
        widget.set_relief(Gtk.ReliefStyle.NORMAL)

    def leave_stack_button(self, widget, event):
        """
        Clear focus when cursor leaves widget.
        """
        if self.stack_active_button != widget:
            widget.set_relief(Gtk.ReliefStyle.NONE)


# ------------------------------------------------------------------------
#
# LastChangedService class
#
# The general idea here is to share the last change history across any
# copies of the Gramplet that are running to avoid having to reparse the
# the database each time one initializes.
#
# ------------------------------------------------------------------------
class LastChangedService(Callback):
    """
    A singleton for centrally sharing changed object history across gramplets.
    """

    __signals__ = {"change-notification": ()}

    __slots__ = (
        "change_history",
        "dbstate",
        "dbid",
        "depth",
        "history_lock",
        "signal_map",
    )

    __init = False

    def __new__(cls, *args):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(LastChangedService, cls).__new__(cls)
        return cls.instance

    def __init__(self, dbstate, uistate, depth=25):
        """
        Initialize the class if needed.
        """
        if not self.__init:
            Callback.__init__(self)
            self.dbstate = dbstate
            self.dbid = None
            self.signal_map = {}
            self.change_history = {}
            self.history_lock = Lock()
            self.depth = depth
            for obj_type in SERIALIZATION_INDEX:
                self.__register_signals(obj_type)
            #            self.__init_signals()
            self.dbstate.connect("database-changed", self.__init_signals)
            uistate.connect("nameformat-changed", self.rebuild_name_labels)
            uistate.connect("placeformat-changed", self.rebuild_place_labels)
            self.__init = True

    def __init_signals(self, *args):
        """
        Connect to signals from database.
        """
        for sig, callback in self.signal_map.items():
            self.dbstate.db.connect(sig, callback)

    def __register_signals(self, object_type):
        """
        Register signal.
        """
        update_function = lambda x: self.update_change_history(x, object_type)
        delete_function = lambda x: self.delete_change_history(x, object_type)
        lower_type = object_type.lower()
        for sig in ["add", "update", "rebuild"]:
            self.signal_map["{}-{}".format(lower_type, sig)] = update_function
        self.signal_map["{}-delete".format(lower_type)] = delete_function

    def set_change_history(self, history):
        """
        Set the history.
        Callers should lock and unlock around this.
        """
        self.dbid = self.dbstate.db.get_dbid()
        self.change_history = history

    def get_change_history(self):
        """
        Fetch the history.
        Callers should lock and unlock around this.
        """
        if not self.dbstate.is_open():
            return {}
        if self.dbid != self.dbstate.db.get_dbid():
            return {}
        if (
            "Global" in self.change_history
            and not self.change_history["Global"]
        ):
            return {}
        return self.change_history

    def update_change_history(self, object_handles, object_type):
        """
        Update history and emit object modification signal.
        """
        if object_handles:
            self.history_lock.acquire()
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
            self.history_lock.release()
            self.emit("change-notification", ())

    def rebuild_labels(self, category):
        """
        Rebuild labels for a formatting change and trigger synthetic update.
        """
        self.history_lock.acquire()
        for (
            index,
            (object_type, object_handle, object_label, change, change_string),
        ) in enumerate(self.change_history[category]):
            object_label, dummy_object = get_object_label(
                self.dbstate.db, object_type, object_handle
            )
            updated_tuple = (
                object_type,
                object_handle,
                object_label,
                change,
                change_string,
            )
            self.change_history[category][index] = updated_tuple
            self.replace_global_label(object_handle, updated_tuple)
        self.history_lock.release()
        self.emit("change-notification", ())

    def replace_global_label(self, object_handle, updated_tuple):
        """
        Replace a label in the Global history.
        """
        for (index, object_data) in enumerate(self.change_history["Global"]):
            if object_data[1] == object_handle:
                self.change_history["Global"][index] = updated_tuple
                break

    def rebuild_name_labels(self):
        """
        Rebuild labels for a name format change.
        """
        self.rebuild_labels("Person")

    def rebuild_place_labels(self):
        """
        Rebuild labels for a place format change and trigger synthetic update.
        """
        self.rebuild_labels("Place")

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
                self.history_lock.acquire()
                self.change_history = {}
                self.history_lock.release()
                self.emit("change-notification", ())

    def check_removed_object(self, object_type, object_handle):
        """
        Check if deleted handle in current history.
        """
        for object_data in self.change_history[object_type]:
            if object_data[1] == object_handle:
                return True
        return False


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
