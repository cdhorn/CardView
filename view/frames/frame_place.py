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
from .frame_utils import TextLink

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

    def __init__(self, grstate, context, place, groups=None):
        PrimaryGrampsFrame.__init__(
            self, grstate, context, place, groups=groups
        )

        place_name = place_displayer.display(grstate.dbstate.db, place)
        title = TextLink(
            place_name,
            "Place",
            place.get_handle(),
            self.switch_object,
            bold=True,
        )
        self.title.pack_start(title, True, False, 0)

        if place.get_type():
            text = glocale.translation.sgettext(place.get_type().xml_str())
            if text:
                self.add_fact(self.make_label(text))

        if place.get_latitude():
            text = "{}: {}".format(_("Latitude"), place.get_latitude())
            self.add_fact(self.make_label(text))
        if place.get_longitude():
            text = "{}: {}".format(_("Longitude"), place.get_longitude())
            self.add_fact(self.make_label(text))

        if place.get_code():
            label = self.make_label(place.get_code(), left=False)
            self.metadata.pack_start(label, False, False, 0)

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()
