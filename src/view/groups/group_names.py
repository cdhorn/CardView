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
NamesFrameGroup
"""

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..frames import NameFrame
from .group_list import FrameGroupList


# ------------------------------------------------------------------------
#
# NamesFrameGroup Class
#
# ------------------------------------------------------------------------
class NamesFrameGroup(FrameGroupList):
    """
    The NamesFrameGroup class provides a container for managing
    all of the addresses a person or repository may have.
    """

    def __init__(self, grstate, groptions, obj):
        FrameGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=False
        )
        frame = NameFrame(
            grstate,
            groptions,
            obj,
            obj.get_primary_name(),
        )
        self.add_frame(frame)

        for name in obj.get_alternate_names():
            frame = NameFrame(grstate, groptions, obj, name)
            self.add_frame(frame)
        self.show_all()