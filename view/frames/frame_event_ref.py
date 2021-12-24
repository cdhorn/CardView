#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
EventRefGrampsFrame.
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.utils.db import family_name
from gramps.gui.editors import EditEventRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import menu_item
from .frame_event import EventGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventRefGrampsFrame class
#
# ------------------------------------------------------------------------
class EventRefGrampsFrame(EventGrampsFrame):
    """
    The EventRefGrampsFrame exposes some of the basic facts about an Event
    for a Person or Family
    """

    def __init__(self, grstate, groptions, obj, event_ref):
        event = grstate.fetch("Event", event_ref.ref)
        reference_tuple = (obj, event_ref)
        EventGrampsFrame.__init__(
            self, grstate, groptions, event, reference_tuple=reference_tuple
        )
        if not groptions.ref_mode:
            return

        if (
            groptions.relation
            and groptions.relation.get_handle()
            != self.reference_base.obj.get_handle()
        ):
            name = None
            if self.reference_base.obj_type == "Person":
                name = name_displayer.display(self.reference_base.obj)
            elif self.reference_base.obj_type == "Family":
                name = family_name(self.reference_base.obj, grstate.dbstate.db)
            if name:
                text = "".join(("[", name, "]"))
                self.ref_widgets["body"].pack_start(
                    self.get_label(text), False, False, 0
                )

        vbox = Gtk.VBox(halign=Gtk.Align.START, hexpand=False)
        vbox.pack_start(
            self.get_label(str(event_ref.get_role())), False, False, 0
        )
        self.ref_widgets["body"].pack_start(vbox, False, False, 0)

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for the event reference.
        """
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(menu_item("gtk-edit", label, self.edit_event_ref))
        label = " ".join((_("Delete"), _("reference")))
        context_menu.append(
            menu_item(
                "list-remove",
                label,
                self.remove_participant,
                self.reference_base.obj,
                self.reference.obj,
            )
        )

    def edit_event_ref(self, *_dummy_obj):
        """
        Launch the desired editor based on object type.
        """
        try:
            EditEventRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.primary.obj,
                self.reference.obj,
                self.save_ref,
            )
        except WindowActiveError:
            pass
