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
PlacesGrampsFrameGroup
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
from ..frames.frame_place_ref import PlaceRefGrampsFrame
from .group_list import GrampsFrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlacesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class PlacesGrampsFrameGroup(GrampsFrameGroupList):
    """
    A container for managing a list of enclosed places.
    """

    def __init__(self, grstate, groptions, place):
        GrampsFrameGroupList.__init__(self, grstate, groptions, place)
        groptions.set_backlink(place.get_handle())
        groptions.option_space = "options.group.place"
        groptions.set_ref_mode(
            grstate.config.get(
                "".join((groptions.option_space, ".reference-mode"))
            )
        )
        self.maximum = grstate.config.get(
            "options.global.max.places-per-group"
        )
        recurse = grstate.config.get(
            "options.group.place.show-all-enclosed-places"
        )
        place_list = []
        self.build_enclosed_place_list(
            place_list, place.get_handle(), recurse=recurse
        )

        for (place, place_ref) in place_list:
            profile = PlaceRefGrampsFrame(grstate, groptions, place, place_ref)
            self.add_frame(profile)
        self.show_all()

    def build_enclosed_place_list(self, place_list, handle, recurse=False):
        """
        Build a list of enclosed places.
        """
        for (
            obj_type,
            obj_handle,
        ) in self.grstate.dbstate.db.find_backlink_handles(handle):
            if obj_type == "Place":
                if len(place_list) >= self.maximum:
                    return
                place = self.fetch("Place", obj_handle)
                for place_ref in place.get_placeref_list():
                    if place_ref.ref == handle:
                        place_list.append((place, place_ref))
                        if recurse:
                            self.build_enclosed_place_list(
                                place_list, obj_handle, recurse=recurse
                            )
        return
