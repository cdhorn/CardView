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
PlaceGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import displayer as place_displayer

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlaceGrampsFrame Class
#
# ------------------------------------------------------------------------
class PlaceGrampsFrame(PrimaryGrampsFrame):
    """
    The PlaceGrampsFrame exposes some of the basic facts about a Place.
    """

    def __init__(self, grstate, groptions, place):
        PrimaryGrampsFrame.__init__(self, grstate, groptions, place)

        place_name = place_displayer.display(grstate.dbstate.db, place)
        title = self.get_link(
            place_name,
            "Place",
            place.get_handle(),
        )
        self.widgets["title"].pack_start(title, True, False, 0)

        if place.get_type():
            text = glocale.translation.sgettext(place.get_type().xml_str())
            if text:
                self.add_fact(
                    self.get_label(text), label=self.get_label(_("Type"))
                )
        if place.get_code():
            self.add_fact(
                self.get_label(place.get_code()),
                label=self.get_label(_("Code")),
            )

        if place.get_latitude():
            text = place.get_latitude()
        else:
            text = "".join(("[", _("Missing"), " ", _("Latitude"), "]"))
        self.add_fact(
            self.get_label(text), label=self.get_label(_("Latitude"))
        )
        if place.get_longitude():
            text = place.get_longitude()
        else:
            text = "".join(("[", _("Missing"), " ", _("Longitude"), "]"))
        self.add_fact(
            self.get_label(text), label=self.get_label(_("Longitude"))
        )

        if place.get_alternative_names():
            for alternate_name in place.get_alternative_names():
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

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)
