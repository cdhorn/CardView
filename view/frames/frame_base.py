#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
GrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
import pickle
import re

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Span
from gramps.gen.utils.db import navigation_label
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import WarningDialog
from gramps.gui.utils import match_primary_mask

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_classes import GrampsContext, GrampsObject
from ..common.common_const import (
    BUTTON_MIDDLE,
    BUTTON_PRIMARY,
    BUTTON_SECONDARY,
)
from ..common.common_utils import button_pressed, button_released
from ..menus.menu_bookmarks import build_bookmarks_menu
from ..menus.menu_config import build_config_menu
from .frame_view import FrameView
from .frame_window import FrameDebugWindow

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsFrame Class
#
# ------------------------------------------------------------------------
class GrampsFrame(FrameView):
    """
    Provides core methods for working with the Gramps objects it manages.
    """

    def __init__(self, grstate, groptions, primary_obj, reference_tuple=None):
        if reference_tuple:
            (base_obj, reference_obj) = reference_tuple
            self.reference_base = GrampsObject(base_obj)
            self.reference = GrampsObject(reference_obj)
        else:
            self.reference_base = None
            self.reference = None
        FrameView.__init__(self, grstate, groptions, self.switch_object)
        self.primary = GrampsObject(primary_obj)
        self.secondary = None
        self.focus = self.primary
        self.dnd_drop_targets = []
        self.css = ""
        if not groptions.bar_mode:
            self.init_layout()
        self.eventbox.connect("button-press-event", self.cb_button_pressed)
        self.eventbox.connect("button-release-event", self.cb_button_released)

    def get_context(self):
        """
        Return self context.
        """
        return GrampsContext(
            self.primary, self.reference, self.secondary, self.reference_base
        )

    def get_title(self):
        """
        Generate a title describing the framed object.
        """
        if not self.primary.has_handle:
            title = self.primary.obj_lang
            if self.secondary:
                title = "".join((title, ": ", self.secondary.obj_lang))
            return title
        title, dummy_obj = navigation_label(
            self.grstate.dbstate.db,
            self.primary.obj_type,
            self.primary.obj.get_handle(),
        )
        if self.reference:
            return "".join((title, ": ", self.reference.obj_lang))
        if self.secondary:
            return "".join((title, ": ", self.secondary.obj_lang))
        return title

    def enable_drag(self, obj=None, eventbox=None, drag_data_get=None):
        """
        Enable self as a drag source.
        """
        obj = obj or self.focus
        eventbox = eventbox or self.eventbox
        drag_data_get = drag_data_get or self.drag_data_get
        if eventbox:
            eventbox.drag_source_set(
                Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY
            )
            target_list = Gtk.TargetList.new([])
            target_list.add(
                obj.dnd_type.atom_drag_type,
                obj.dnd_type.target_flags,
                obj.dnd_type.app_id,
            )
            eventbox.drag_source_set_target_list(target_list)
            eventbox.drag_source_set_icon_name(obj.dnd_icon)
            eventbox.connect("drag_data_get", drag_data_get)

    def drag_data_get(
        self, _dummy_widget, _dummy_context, data, info, _dummy_time
    ):
        """
        Return requested data.
        """
        if info == self.focus.dnd_type.app_id:
            returned_data = (
                self.focus.dnd_type.drag_type,
                id(self),
                self.focus.obj.get_handle(),
                0,
            )
            data.set(
                self.focus.dnd_type.atom_drag_type,
                8,
                pickle.dumps(returned_data),
            )

    def enable_drop(self, eventbox, dnd_drop_targets, drag_data_received):
        """
        Enable self as a basic drop target.
        """
        if self.focus.has_notes or self.primary.obj_type == "Note":
            for target in DdTargets.all_text_targets():
                dnd_drop_targets.append(target)
            dnd_drop_targets.append(Gtk.TargetEntry.new("text/html", 0, 7))
        if self.focus.has_notes:
            dnd_drop_targets.append(DdTargets.NOTE_LINK.target())
        if self.primary.has_media:
            dnd_drop_targets.append(DdTargets.MEDIAOBJ.target())
        if self.focus.has_attributes:
            dnd_drop_targets.append(DdTargets.ATTRIBUTE.target())
        if self.focus.has_citations:
            dnd_drop_targets.append(DdTargets.CITATION_LINK.target())
            dnd_drop_targets.append(DdTargets.SOURCE_LINK.target())
        if self.focus.has_urls:
            dnd_drop_targets.append(DdTargets.URL.target())
            dnd_drop_targets.append(DdTargets.URI_LIST.target())
            dnd_drop_targets.append(Gtk.TargetEntry.new("URL", 0, 8))
        eventbox.drag_dest_set(
            Gtk.DestDefaults.ALL, dnd_drop_targets, Gdk.DragAction.COPY
        )
        eventbox.connect("drag-data-received", drag_data_received)

    def drag_data_received(
        self,
        _dummy_widget,
        _dummy_context,
        _dummy_x,
        _dummy_y,
        data,
        _dummy_info,
        _dummy_time,
    ):
        """
        Handle dropped data, override in derived classes as needed.
        """
        if data and data.get_data():
            try:
                dnd_type, obj_id, obj_or_handle, dummy_var1 = pickle.loads(
                    data.get_data()
                )
            except pickle.UnpicklingError:
                return self._dropped_text(data.get_data().decode("utf-8"))
            if id(self) != obj_id:
                return self._child_drop_handler(dnd_type, obj_or_handle, data)
        return False

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing, should be defined in derived classes.
        """

    def _base_drop_handler(self, dnd_type, obj_or_handle, _dummy_data):
        """
        Handle drop processing largely common to all objects.
        """
        if DdTargets.CITATION_LINK.drag_type == dnd_type:
            action = action_handler(
                "Citation", self.grstate, None, self.primary, self.focus
            )
            action.added_citation(obj_or_handle)
            return True
        if DdTargets.SOURCE_LINK.drag_type == dnd_type:
            action = action_handler(
                "Citation", self.grstate, None, self.primary, self.focus
            )
            action.add_new_citation(obj_or_handle)
            return True
        if DdTargets.NOTE_LINK.drag_type == dnd_type:
            action = action_handler(
                "Note", self.grstate, None, self.primary, self.focus
            )
            action.added_note(obj_or_handle)
            return True
        return False

    def _dropped_text(self, data):
        """
        Examine and try to handle dropped text in a reasonable manner.
        """
        if self._try_add_new_media(data):
            return True
        added_urls = self._try_add_new_urls(data)
        if not added_urls or (len(data) > (2 * added_urls)):
            if self.focus.has_notes:
                action = action_handler(
                    "Note", self.grstate, None, self.primary, self.focus
                )
                action.set_content(data)
                action.add_new_note()
                return True
            if self.focus.obj_type == "Note":
                action = action_handler("Note", self.grstate, self.focus)
                action.set_content(data)
                action.update_note()
                return True
        elif added_urls:
            return True
        return False

    def _try_add_new_media(self, data):
        """
        Handle a local media drop.
        """
        if self.focus.has_media:
            links = re.findall(r"(?P<url>file?://[^\s]+)", data)
            if links:
                for link in links:
                    action = action_handler(
                        "Media", self.grstate, None, self.primary
                    )
                    action.set_media_file_path(link)
                    action.add_new_media()
                return True
        return False

    def _try_add_new_urls(self, data):
        """
        Handle dropped urls.
        """
        added_urls = 0
        if self.focus.has_urls:
            links = re.findall(r"(?P<url>https?://[^\s]+)", data)
            if links:
                for link in links:
                    action = action_handler(
                        "Url", self.grstate, None, self.primary, self.focus
                    )
                    action.set_path(link)
                    action.add_url()
                    added_urls = added_urls + len(link)
        return added_urls

    def load_age(self, base_date, current_date):
        """
        Calculate and show age.
        """
        if "age" in self.widgets:
            span = Span(base_date, current_date)
            if span.is_valid():
                year = str(current_date.get_year())
                precision = global_config.get(
                    "preferences.age-display-precision"
                )
                age = str(span.format(precision=precision).strip("()"))
                if age[:2] == "0 ":
                    age = ""
                text = "".join(
                    ("<b>", year, "</b>\n", age.replace(", ", ",\n"))
                )
                label = Gtk.Label(
                    label=self.detail_markup.format(text.strip()),
                    use_markup=True,
                    justify=Gtk.Justification.CENTER,
                )
                self.widgets["age"].pack_start(label, False, False, 0)

    def cb_button_pressed(self, obj, event):
        """
        Handle button pressed.
        """
        if not self.primary.is_primary:
            return True
        if button_pressed(event, BUTTON_SECONDARY):
            if match_primary_mask(event.get_state()):
                build_bookmarks_menu(self, self.grstate, event)
                return True
            self.build_context_menu(obj, event)
            return True
        if button_pressed(event, BUTTON_PRIMARY):
            return False
        if button_pressed(event, BUTTON_MIDDLE):
            build_config_menu(
                self,
                self.grstate,
                self.groptions,
                self.primary.obj_type,
                event,
            )
            return True
        return False

    def cb_button_released(self, obj, event):
        """
        Handle button released.
        """
        if not self.primary.is_primary:
            return True
        if button_released(event, BUTTON_PRIMARY):
            if match_primary_mask(event.get_state()):
                self._dump_context()
                return True
            self.switch_object(None, None, self.focus.obj_type, self.focus.obj)
            return True
        return False

    def switch_object(self, _dummy_obj, _dummy_event, obj_type, obj_or_handle):
        """
        Change active object for the view.
        """
        if "Ref" in obj_type:
            context = GrampsContext(self.primary, obj_or_handle, None)
        elif obj_type in ["Address", "Attribute", "Name", "Url", "LdsOrd"]:
            context = GrampsContext(self.primary, None, obj_or_handle)
        else:
            if isinstance(obj_or_handle, str):
                obj = self.grstate.fetch(obj_type, obj_or_handle)
            else:
                obj = obj_or_handle
            context = GrampsContext(obj, None, None)
        return self.grstate.load_page(context.pickled)

    def _dump_context(self, *_dummy_args):
        """
        Dump context.
        """
        try:
            FrameDebugWindow(self.grstate, self.get_context())
        except WindowActiveError:
            WarningDialog(
                _("Could Not Open Context Object View"),
                _(
                    "A context object view window is already "
                    "open, close it before launching a new one."
                ),
                parent=self.grstate.uistate.window,
            )

    def build_context_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click, should be defined in
        derived classes.
        """
        return True

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("display.border-width")
        color = self.get_color_css()
        self.css = "".join(
            (".frame { border-width: ", str(border), "px; ", color, " }")
        ).encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(self.css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
        if self.groptions.ref_mode in [2, 4]:
            context = self.ref_frame.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            context.add_class("frame")

    def get_color_css(self):
        """
        For derived objects to set their color scheme if in use.
        """
        scheme = global_config.get("colors.scheme")
        background = self.grstate.config.get(
            "display.default-background-color"
        )
        return "".join(("background-color: ", background[scheme], ";"))

    def get_css_style(self):
        """
        Return css style string.
        """
        return self.css
