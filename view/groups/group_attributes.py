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
AttributesGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_attribute import AttributeGrampsFrame
from ..frames.frame_utils import get_gramps_object_type
from .group_list import GrampsFrameGroupList


# ------------------------------------------------------------------------
#
# AttributesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class AttributesGrampsFrameGroup(GrampsFrameGroupList):
    """
    The AttributesGrampsFrameGroup class provides a container for managing
    all of the attributes an object may have.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(
            self, grstate, groptions, enable_drop=False
        )
        self.obj = obj
        self.obj_type = get_gramps_object_type(self.obj)
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        for attribute in obj.get_attribute_list():
            frame = AttributeGrampsFrame(grstate, groptions, obj, attribute)
            self.add_frame(frame)
        self.show_all()
