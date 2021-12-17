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
PlaceRefGrampsFrame
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
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditPlaceRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import menu_item
from .frame_place import PlaceGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlaceRefGrampsFrame class
#
# ------------------------------------------------------------------------
class PlaceRefGrampsFrame(PlaceGrampsFrame):
    """
    The PlaceRefGrampsFrame exposes some of the basic facts about an
    enclosed Place.
    """

    def __init__(
        self,
        grstate,
        groptions,
        place,
        place_ref,
    ):
        enclosed_place = grstate.fetch("Place", place_ref.ref)
        PlaceGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            place,
            reference_tuple=(enclosed_place, place_ref),
        )
        if not groptions.ref_mode:
            return

        vbox = None
        date = glocale.date_displayer.display(place_ref.get_date_object())
        if not date:
            date = _("[None Provided]")
        left = groptions.ref_mode == 1
        if groptions.ref_mode in [1, 3]:
            self.ref_widgets["body"].pack_start(
                self.get_label(_("Date"), left=left), False, False, 0
            )
            self.ref_widgets["body"].pack_start(
                self.get_label(date, left=left), False, False, 0
            )
        else:
            vbox = Gtk.VBox()
            vbox.pack_start(
                self.get_label(": ".join((_("Date"), date))),
                True,
                True,
                0,
            )
        if vbox:
            self.ref_widgets["body"].pack_start(vbox, True, True, 0)

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for an associate.
        """
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(menu_item("gtk-edit", label, self.edit_place_ref))
        label = " ".join((_("Delete"), _("reference")))
        context_menu.append(
            menu_item(
                "list-remove",
                label,
                self.remove_place_ref,
                self.reference.obj,
            )
        )

    def edit_place_ref(self, *_dummy_obj):
        """
        Launch the editor.
        """
        try:
            EditPlaceRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.primary.obj,
                self.reference.obj,
                self.save_ref,
            )
        except WindowActiveError:
            pass

    def remove_place_ref(self, _dummy_obj, place_ref):
        """
        Remove an enclosed place reference.
        """
        place = self.fetch("Place", place_ref.ref)
        text = place_displayer.display(
            self.grstate.dbstate.db, self.primary.obj
        )
        prefix = _(
            "You are about to remove the following enclosed place from this "
            "place:"
        )
        extra = _(
            "Note this does not delete the place. You can also use the "
            "undo option under edit if you change your mind later."
        )
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            new_list = []
            for ref in self.primary.obj.get_placeref_list():
                if not ref.ref == place_ref.ref:
                    new_list.append(ref)
            message = " ".join(
                (
                    _("Removed"),
                    _("PlaceRef"),
                    place.get_gramps_id(),
                    _("from"),
                    _("Place"),
                    self.primary.obj.get_gramps_id(),
                )
            )
            self.primary.obj.set_placeref_list(new_list)
            self.primary.commit(self.grstate, message)
