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
AttributesCardGroup
"""

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..cards import AttributeCard
from .group_list import CardGroupList


# ------------------------------------------------------------------------
#
# AttributesCardGroup Class
#
# ------------------------------------------------------------------------
class AttributesCardGroup(CardGroupList):
    """
    The AttributesCardGroup class provides a container for managing
    all of the attributes an object may have.
    """

    def __init__(self, grstate, groptions, obj):
        CardGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=False
        )
        for attribute in obj.attribute_list:
            card = AttributeCard(grstate, groptions, obj, attribute)
            self.add_card(card)
        self.show_all()
