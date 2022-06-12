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
EnclosingPlacesCardGroup and EnclosedPlacesCardGroup
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..cards import PlaceRefCard
from .group_list import CardGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EnclosingPlacesCardGroup Class
#
# ------------------------------------------------------------------------
class EnclosingPlacesCardGroup(CardGroupList):
    """
    A container for managing a list of enclosing places.
    """

    def __init__(self, grstate, groptions, place):
        CardGroupList.__init__(self, grstate, groptions, place)
        groptions.option_space = "group.place"
        groptions.set_ref_mode(
            grstate.config.get("%s.reference-mode" % groptions.option_space)
        )
        place_list = []
        self.build_enclosing_place_list(place_list, place.handle)
        place_list.reverse()

        for (list_place, list_place_ref) in place_list:
            profile = PlaceRefCard(
                grstate, groptions, list_place, list_place_ref
            )
            self.add_card(profile)
        self.show_all()

    def build_enclosing_place_list(self, place_list, handle):
        """
        Build a list of enclosing places.
        """
        place = self.fetch("Place", handle)
        for place_ref in place.placeref_list:
            found = False
            for (list_place, dummy_list_place_ref) in place_list:
                if list_place.handle == place_ref.ref:
                    found = True
                    break
            if found:
                continue
            ref_place = self.fetch("Place", place_ref.ref)
            place_list.append((ref_place, place_ref))
            self.build_enclosing_place_list(place_list, place_ref.ref)


# ------------------------------------------------------------------------
#
# EnclosedPlacesCardGroup Class
#
# ------------------------------------------------------------------------
class EnclosedPlacesCardGroup(CardGroupList):
    """
    A container for managing a list of enclosed places.
    """

    def __init__(self, grstate, groptions, place):
        CardGroupList.__init__(self, grstate, groptions, place)
        groptions.set_backlink(place.handle)
        groptions.option_space = "group.place"
        groptions.set_ref_mode(
            grstate.config.get("%s.reference-mode" % groptions.option_space)
        )
        self.maximum = grstate.config.get("group.place.max-per-group")
        recurse = grstate.config.get("group.place.show-all-enclosed-places")
        place_list = []
        self.build_enclosed_place_list(
            place_list, place.handle, recurse=recurse
        )

        for (list_place, list_place_ref) in place_list:
            profile = PlaceRefCard(
                grstate, groptions, list_place, list_place_ref
            )
            self.add_card(profile)
        self.show_all()

    def build_enclosed_place_list(self, place_list, handle, recurse=False):
        """
        Build a list of enclosed places.
        """
        db = self.grstate.dbstate.db
        for (dummy_obj_type, obj_handle) in db.find_backlink_handles(
            handle, ["Place"]
        ):
            if len(place_list) < self.maximum:
                place = db.get_place_from_handle(obj_handle)
                for place_ref in place.placeref_list:
                    if place_ref.ref == handle:
                        place_list.append((place, place_ref))
                        if recurse:
                            self.build_enclosed_place_list(
                                place_list, obj_handle, recurse=recurse
                            )
