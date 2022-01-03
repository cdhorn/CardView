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
PlaceRefFrame
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..actions import PlaceAction
from ..menus.menu_utils import menu_item
from .frame_place import PlaceFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlaceRefFrame class
#
# ------------------------------------------------------------------------
class PlaceRefFrame(PlaceFrame):
    """
    The PlaceRefFrame exposes some of the basic facts about an
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
        PlaceFrame.__init__(
            self,
            grstate,
            groptions,
            place,
            reference_tuple=(enclosed_place, place_ref),
        )
        if groptions.ref_mode:
            date = glocale.date_displayer.display(place_ref.get_date_object())
            if not date:
                date = _("[None Provided]")
            self.add_ref_item(_("Date"), date)
            self.show_ref_items()

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for an associate.
        """
        action = PlaceAction(self.grstate, self.primary, self.reference)
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(menu_item("gtk-edit", label, action.edit_place))
        label = " ".join((_("Delete"), _("reference")))
        context_menu.append(
            menu_item(
                "list-remove",
                label,
                action.remove_place_reference,
            )
        )
