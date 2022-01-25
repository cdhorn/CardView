#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021       Christopher Horn
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
ReferenceFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import pickle

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.ddtargets import DdTargets
from gramps.gui.utils import match_primary_mask

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_classes import GrampsContext
from ..common.common_const import (
    BUTTON_MIDDLE,
    BUTTON_PRIMARY,
    BUTTON_SECONDARY,
)
from ..common.common_utils import (
    button_pressed,
    button_released,
)
from ..menus.menu_config import build_config_menu
from ..menus.menu_utils import (
    add_attributes_menu,
    add_citations_menu,
    add_notes_menu,
    add_privacy_menu_option,
    add_double_separator,
    show_menu,
)
from .frame_primary import PrimaryFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ReferenceFrame class
#
# ------------------------------------------------------------------------
class ReferenceFrame(PrimaryFrame):
    """
    The ReferenceFrame class provides support for object References.
    """

    def __init__(self, grstate, groptions, primary_obj, reference_tuple=None):
        PrimaryFrame.__init__(
            self,
            grstate,
            groptions,
            primary_obj,
            reference_tuple=reference_tuple,
        )
        self.ref_vbox = None
        self.dnd_drop_ref_targets = []
        if not reference_tuple or not groptions.ref_mode:
            return

        if self.reference.obj_type not in ["PlaceRef"]:
            self.ref_widgets["id"].load(
                self.reference,
                gramps_id=self.primary.obj.get_gramps_id(),
            )
            self.ref_widgets["icons"].load(
                self.reference,
                title=self.get_title(),
            )
        self.ref_eventbox.connect(
            "button-press-event", self.cb_ref_button_pressed
        )
        self.ref_eventbox.connect(
            "button-release-event", self.cb_ref_button_released
        )

        self.enable_drag(
            obj=self.reference,
            eventbox=self.ref_eventbox,
            drag_data_get=self.ref_drag_data_get,
        )

    def ref_enable_drop(self, eventbox, dnd_drop_targets, drag_data_received):
        """
        Enabled self as a basic drop target.
        """
        if self.reference.has_notes:
            for target in DdTargets.all_text_targets():
                dnd_drop_targets.append(target)
            dnd_drop_targets.append(Gtk.TargetEntry.new("text/html", 0, 7))
            dnd_drop_targets.append(DdTargets.NOTE_LINK.target())
        if self.reference.has_attributes:
            dnd_drop_targets.append(DdTargets.ATTRIBUTE.target())
        if self.reference.has_citations:
            dnd_drop_targets.append(DdTargets.CITATION_LINK.target())
            dnd_drop_targets.append(DdTargets.SOURCE_LINK.target())
        eventbox.drag_dest_set(
            Gtk.DestDefaults.ALL, dnd_drop_targets, Gdk.DragAction.COPY
        )
        eventbox.connect("drag-data-received", drag_data_received)

    def ref_drag_data_get(
        self, _dummy_widget, _dummy_context, data, info, _dummy_time
    ):
        """
        Return requested data.
        """
        if info == self.reference.dnd_type.app_id:
            returned_data = (
                self.reference.dnd_type.drag_type,
                id(self),
                self.reference.obj,
                0,
            )
            data.set(
                self.reference.dnd_type.atom_drag_type,
                8,
                pickle.dumps(returned_data),
            )

    def ref_drag_data_received(
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
        Handle dropped data.
        """
        if data and data.get_data():
            try:
                dnd_type, obj_id, obj_or_handle, dummy_var1 = pickle.loads(
                    data.get_data()
                )
            except pickle.UnpicklingError:
                return self.dropped_ref_text(data.get_data().decode("utf-8"))
            if id(self) != obj_id:
                return self._ref_child_drop_handler(
                    dnd_type, obj_or_handle, data
                )
        return False

    def _ref_child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing, override in derived classes as needed.
        """
        self._ref_base_drop_handler(dnd_type, obj_or_handle, data)

    def _ref_base_drop_handler(self, dnd_type, obj_or_handle, _dummy_data):
        """
        Handle drop processing largely common to all objects.
        """
        if DdTargets.NOTE_LINK.drag_type == dnd_type:
            action = action_handler(
                "Note",
                self.grstate,
                None,
                self.reference_base,
                self.reference,
            )
            action.added_note(obj_or_handle)
            return True
        if DdTargets.CITATION_LINK.drag_type == dnd_type:
            action = action_handler(
                "Citation",
                self.grstate,
                None,
                self.reference_base,
                self.reference,
            )
            action.added_citation(obj_or_handle)
            return True
        if DdTargets.SOURCE_LINK.drag_type == dnd_type:
            action = action_handler(
                "Citation",
                self.grstate,
                None,
                self.reference_base,
                self.reference,
            )
            action.add_new_citation(obj_or_handle)
            return True
        return False

    def dropped_ref_text(self, data):
        """
        Examine and try to handle dropped text in a reasonable manner.
        """
        if data and self.reference.has_notes:
            action = action_handler(
                "Note", self.grstate, None, self.reference_base, self.reference
            )
            action.set_content(data)
            action.add_new_note()
            return True
        return False

    def cb_ref_button_pressed(self, obj, event):
        """
        Handle button pressed.
        """
        if button_pressed(event, BUTTON_SECONDARY):
            self.build_ref_context_menu(obj, event)
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

    def cb_ref_button_released(self, obj, event):
        """
        Handle button release.
        """
        if button_released(event, BUTTON_PRIMARY):
            if match_primary_mask(event.get_state()):
                self._dump_context()
                return True
            page_context = GrampsContext(
                self.reference_base, self.reference, None
            )
            self.grstate.load_page(page_context.pickled)
            return True
        return False

    def build_ref_context_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click on a reference object.
        """
        context_menu = Gtk.Menu()
        self.add_ref_custom_actions(context_menu)
        add_attributes_menu(
            self.grstate, context_menu, self.reference_base, self.reference
        )
        add_citations_menu(
            self.grstate,
            context_menu,
            self.reference_base,
            self.reference,
        )
        add_notes_menu(
            self.grstate, context_menu, self.reference_base, self.reference
        )
        add_privacy_menu_option(
            self.grstate, context_menu, self.reference_base, self.reference
        )
        add_double_separator(context_menu)
        reference_type = self._get_reference_type()
        label = Gtk.MenuItem(label=reference_type)
        label.set_sensitive(False)
        context_menu.append(label)
        return show_menu(context_menu, self, event)

    def add_ref_custom_actions(self, context_menu):
        """
        For derived objects to inject their own actions into the menu.
        """

    def _get_reference_type(self):
        """
        Return textual string describing reference type.
        """
        if self.reference.obj_type == "ChildRef":
            text = _("Child")
        elif self.reference.obj_type == "PersonRef":
            text = _("Person")
        elif self.reference.obj_type == "EventRef":
            text = _("Event")
        elif self.reference.obj_type == "RepoRef":
            text = _("Repository")
        elif self.reference.obj_type == "MediaRef":
            text = _("Media")
        elif self.reference.obj_type == "PlaceRef":
            text = _("Place")
        return " ".join((text, _("reference")))

    def add_ref_item(self, label, value):
        """
        Add reference item to widget based on reference display mode.
        """
        ref_mode = self.groptions.ref_mode
        if ref_mode in [1, 3]:
            left = ref_mode == 1
            if label:
                self.ref_widgets["body"].pack_start(
                    self.get_label(label, left=left),
                    False,
                    False,
                    0,
                )
            if value:
                self.ref_widgets["body"].pack_start(
                    self.get_label(value, left=left),
                    False,
                    False,
                    0,
                )
        else:
            if not self.ref_vbox:
                self.ref_vbox = Gtk.VBox(halign=Gtk.Align.START, hexpand=False)
            text = label
            if value:
                if text:
                    text = ": ".join((text, value)).replace("::", ":")
                else:
                    text = value
            self.ref_vbox.pack_start(self.get_label(text), False, False, 0)

    def show_ref_items(self):
        """
        Set horizontal ref widget if needed.
        """
        if self.groptions.ref_mode not in [1, 3]:
            self.ref_widgets["body"].pack_start(self.ref_vbox, True, True, 0)
