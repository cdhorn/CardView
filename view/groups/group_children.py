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
ChildrenFrameGroup
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import ChildRef
from gramps.gui.editors import EditChildRef

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..frames import ChildRefFrame
from .group_list import FrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ChildrenFrameGroup Class
#
# ------------------------------------------------------------------------
class ChildrenFrameGroup(FrameGroupList):
    """
    A container for managing a list of children for a given family.
    """

    def __init__(self, grstate, groptions, family):
        FrameGroupList.__init__(self, grstate, groptions, family)
        context = "child"
        if "parent" in groptions.option_space:
            context = "sibling"

        groptions.set_backlink(family.get_handle())
        groptions.option_space = "".join(("group.", context))
        groptions.set_ref_mode(
            grstate.config.get(
                "".join((groptions.option_space, ".reference-mode"))
            )
        )

        child_number = 0
        number_children = self.grstate.config.get(
            "".join((groptions.option_space, ".number-children"))
        )
        for child_ref in family.get_child_ref_list():
            if number_children:
                child_number = child_number + 1
                groptions.set_number(child_number)
            profile = ChildRefFrame(
                grstate,
                groptions,
                family,
                child_ref,
            )
            self.add_frame(profile)
        self.show_all()

    def save_reordered_list(self):
        """
        Save a reordered list of children.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_child_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
                    break
        message = " ".join(
            (
                _("Reordered Children"),
                _("for"),
                _("Family"),
                self.group_base.obj.get_gramps_id(),
            )
        )
        self.group_base.obj.set_child_ref_list(new_list)
        self.group_base.commit(self.grstate, message)

    def save_new_object(self, handle, insert_row):
        """
        Add a new child to the list of children.
        """
        if self.group_base.obj.get_father_handle() == handle:
            return
        if self.group_base.obj.get_mother_handle() == handle:
            return
        for frame in self.row_frames:
            if frame.primary.obj.get_handle() == handle:
                return

        child_ref = ChildRef()
        child_ref.ref = handle
        callback = lambda x: self.save_new_child(x, insert_row)
        child = self.fetch("Person", handle)
        name = name_displayer.display(child)
        try:
            EditChildRef(
                name,
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                child_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def save_new_child(self, child_ref, insert_row):
        """
        Save the new child added to the list of children.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_child_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
        new_list.insert(insert_row, child_ref)
        child = self.fetch("Person", child_ref.ref)
        message = " ".join(
            (
                _("Added Child"),
                child.get_gramps_id(),
                _("to"),
                _("Family"),
                self.group_base.obj.get_gramps_id(),
            )
        )
        with DbTxn(message, self.grstate.dbstate.db) as trans:
            self.group_base.obj.set_child_ref_list(new_list)
            self.grstate.dbstate.db.commit_family(self.group_base.obj, trans)
            child.add_parent_family_handle(self.group_base.obj.get_handle())
            self.grstate.dbstate.db.commit_person(child, trans)
