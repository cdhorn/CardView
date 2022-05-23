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
PlaceFrame
"""

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import displayer as place_displayer

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..menus.menu_utils import add_enclosed_places_menu
from .frame_reference import ReferenceFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlaceFrame Class
#
# ------------------------------------------------------------------------
class PlaceFrame(ReferenceFrame):
    """
    The PlaceFrame exposes some of the basic facts about a Place.
    """

    def __init__(self, grstate, groptions, place, reference_tuple=None):
        ReferenceFrame.__init__(
            self, grstate, groptions, place, reference_tuple=reference_tuple
        )
        self.__add_place_title(place)
        self.__add_place_type(place)
        self.__add_place_code(place)
        self.__add_place_coordinates(place)
        self.__add_place_alternative_names(place)
        self.enable_drag()
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_place_title(self, place):
        """
        Add place title.
        """
        if "group" in self.groptions.option_space:
            place_name = place_displayer.display(
                self.grstate.dbstate.db, place
            )
            title = self.get_link(
                place_name,
                "Place",
                place.get_handle(),
            )
        else:
            title = self.get_title_breadcrumbs()
        self.widgets["title"].pack_start(title, True, False, 0)

    def __add_place_type(self, place):
        """
        Add place type.
        """
        if place.get_type():
            text = glocale.translation.sgettext(place.get_type().xml_str())
            if text:
                self.add_fact(
                    self.get_label(text), label=self.get_label(_("Type"))
                )

    def __add_place_code(self, place):
        """
        Add place code.
        """
        if place.get_code():
            self.add_fact(
                self.get_label(place.get_code()),
                label=self.get_label(_("Code")),
            )

    def __add_place_coordinates(self, place):
        """
        Add place geographic coordinates.
        """
        if place.get_latitude():
            latitude_text = place.get_latitude()
        else:
            latitude_text = "".join(("[", _("Missing"), "]"))
        if place.get_longitude():
            longitude_text = place.get_longitude()
        else:
            longitude_text = "".join(("[", _("Missing"), "]"))
        text = ", ".join((latitude_text, longitude_text))
        label = ", ".join((_("Latitude"), _("Longitude")))
        self.add_fact(self.get_label(text), label=self.get_label(label))

    def __add_place_alternative_names(self, place):
        """
        Add place alternate names.
        """
        alternative_names = place.get_alternative_names()
        if alternative_names:
            for alternate_name in alternative_names:
                value = alternate_name.get_value()
                if alternate_name.get_language():
                    value = "".join(
                        (value, " (", alternate_name.get_language(), ")")
                    )
                date = glocale.date_displayer.display(
                    alternate_name.get_date_object()
                )
                if not date:
                    date = ""
                date = "  ".join((_("Alternate Name"), date))
                self.add_fact(
                    self.get_label(value),
                    label=self.get_label(date),
                    extra=True,
                )

    def get_title_breadcrumbs(self):
        """
        Return a title widget with linkable parts.
        """
        hbox = Gtk.HBox(hexpand=False, vexpand=False)
        chain = [self.primary.obj]
        self.get_place_chain(chain, self.primary.obj)
        comma_label = None
        for place in chain:
            title = place.get_name().get_value()
            if place.get_type():
                place_type = glocale.translation.sgettext(
                    place.get_type().xml_str()
                )
            else:
                place_type = None
            place_label = self.get_link(
                title, "Place", place.get_handle(), tooltip=place_type
            )
            if comma_label:
                hbox.pack_start(self.get_label(", "), False, False, 0)
            hbox.pack_start(place_label, False, False, 0)
            comma_label = True
        return hbox

    def get_place_chain(self, chain, obj):
        """
        Return list of parent places.
        """
        if obj.get_placeref_list():
            place_ref = obj.get_placeref_list()[0]
            place = self.grstate.fetch("Place", place_ref.ref)
            chain.append(place)
            self.get_place_chain(chain, place)

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def add_custom_actions(self, context_menu):
        """
        Add context menu items unique to a place.
        """
        add_enclosed_places_menu(self.grstate, context_menu, self.primary)
