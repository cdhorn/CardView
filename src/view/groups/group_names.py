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
NamesCardGroup
"""

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..cards import NameCard
from .group_list import CardGroupList


# ------------------------------------------------------------------------
#
# NamesCardGroup Class
#
# ------------------------------------------------------------------------
class NamesCardGroup(CardGroupList):
    """
    The NamesCardGroup class provides a container for managing
    all of the addresses a person or repository may have.
    """

    def __init__(self, grstate, groptions, obj):
        CardGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=False
        )
        card = NameCard(
            grstate,
            groptions,
            obj,
            obj.primary_name,
        )
        self.add_card(card)

        for name in obj.alternate_names:
            card = NameCard(grstate, groptions, obj, name)
            self.add_card(card)
        self.show_all()
