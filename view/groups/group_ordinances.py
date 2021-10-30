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
LDSOrdinancesGrampsFrameGroup
"""

from ..common.common_utils import get_gramps_object_type

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_ordinance import LDSOrdinanceGrampsFrame
from .group_list import GrampsFrameGroupList


# ------------------------------------------------------------------------
#
# LDSOrdinancesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class LDSOrdinancesGrampsFrameGroup(GrampsFrameGroupList):
    """
    The LDSOrdinancesGrampsFrameGroup class provides a container for managing
    all of the ordinances a person or family may have.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(
            self, grstate, groptions, enable_drop=False
        )
        self.obj = obj
        self.obj_type = get_gramps_object_type(obj)
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        for ordinance in obj.get_lds_ord_list():
            frame = LDSOrdinanceGrampsFrame(grstate, groptions, obj, ordinance)
            self.add_frame(frame)
        self.show_all()
