#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022       Christopher Horn
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
PaternalLineageFrameGroup, MaternalLineageFrameGroup
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
from ..common.common_classes import GrampsOptions
from ..frames import FamilyFrame
from .group_list import FrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PaternalLineageFrameGroup Class
#
# ------------------------------------------------------------------------
class PaternalLineageFrameGroup(FrameGroupList):
    """
    A container with a list of paternal ancestors for a person.
    """

    def __init__(self, grstate, groptions, person, maternal=False):
        FrameGroupList.__init__(self, grstate, groptions, person)
        mode = 0
        groptions = GrampsOptions("group.person")
        groptions.maternal_mode = maternal
        if maternal:
            mode = grstate.config.get("group.maternal.display-mode")
        else:
            mode = grstate.config.get("group.paternal.display-mode")
        if mode == 0:
            groptions.force_compact = True
        elif mode == 1:
            groptions.vertical_orientation = False
        else:
            groptions.vertical_orientation = True

        families, dummy_ancestors = self.extract_line(maternal=maternal)
        self.render_families(families, groptions)
        self.show_all()

    def render_families(self, families, groptions):
        """
        Render lineage with family cards.
        """
        for family in families:
            couple_widget = FamilyFrame(
                self.grstate,
                groptions,
                family,
            )
            self.add_frame(couple_widget)

    def extract_line(self, maternal=False):
        """
        Return a set of ordered tuples for a direct line.
        """
        families = []
        ancestors = []
        family_handle = self.group_base.obj.get_main_parents_family_handle()
        while family_handle:
            family = self.grstate.fetch("Family", family_handle)
            families.append(family)
            if not maternal:
                if family.father_handle:
                    father = self.grstate.fetch("Person", family.father_handle)
                    if family.mother_handle:
                        mother = self.grstate.fetch(
                            "Person", family.mother_handle
                        )
                    else:
                        mother = None
                    ancestors.append((father, mother))
                    family_handle = father.get_main_parents_family_handle()
            else:
                if family.mother_handle:
                    mother = self.grstate.fetch("Person", family.mother_handle)
                    if family.father_handle:
                        father = self.grstate.fetch(
                            "Person", family.father_handle
                        )
                    else:
                        father = None
                    ancestors.append((mother, father))
                    family_handle = mother.get_main_parents_family_handle()
        return families, ancestors


# ------------------------------------------------------------------------
#
# MaternalLineageFrameGroup Class
#
# ------------------------------------------------------------------------
class MaternalLineageFrameGroup(PaternalLineageFrameGroup):
    """
    A container with a list of maternal ancestors for a person.
    """

    def __init__(self, grstate, groptions, person):
        PaternalLineageFrameGroup.__init__(
            self, grstate, groptions, person, maternal=True
        )
