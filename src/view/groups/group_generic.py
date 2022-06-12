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
GenericCardGroup
"""

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..cards import (
    CitationCard,
    EventCard,
    FamilyCard,
    MediaCard,
    NoteCard,
    PersonCard,
    PlaceCard,
    RepositoryCard,
    SourceCard,
)
from .group_list import CardGroupList

CARD_MAP = {
    "Person": PersonCard,
    "Family": FamilyCard,
    "Event": EventCard,
    "Place": PlaceCard,
    "Media": MediaCard,
    "Note": NoteCard,
    "Source": SourceCard,
    "Citation": CitationCard,
    "Repository": RepositoryCard,
}


# ------------------------------------------------------------------------
#
# GenericCardGroup Class
#
# ------------------------------------------------------------------------
class GenericCardGroup(CardGroupList):
    """
    The GenericCardGroup class provides a container for managing a
    set of generi..cards for a list of primary Gramps objects.
    """

    def __init__(self, grstate, groptions, card_obj_type, card_obj_handles):
        CardGroupList.__init__(
            self, grstate, groptions, None, enable_drop=False
        )
        self.obj_type = card_obj_type
        self.obj_handles = card_obj_handles

        if card_obj_type == "Tuples":
            tuple_list = card_obj_handles
        else:
            tuple_list = [(card_obj_type, x) for x in card_obj_handles]

        groups = {
            "ref": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "age": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "attributes": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        for obj_type, obj_handle in tuple_list:
            if obj_type not in CARD_MAP:
                continue
            group_space = "group.%s" % obj_type.lower()
            group_groptions = GrampsOptions(group_space, size_groups=groups)
            group_groptions.set_age_base(groptions.age_base)
            obj = self.fetch(obj_type, obj_handle)
            card = CARD_MAP[obj_type](grstate, group_groptions, obj)
            self.add_card(card)
        self.show_all()
