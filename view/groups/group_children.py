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
ChildrenGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from copy import copy

# ------------------------------------------------------------------------
#
# Gramps modules
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
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_child import ChildGrampsFrame
from .group_list import GrampsFrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ChildrenGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class ChildrenGrampsFrameGroup(GrampsFrameGroupList):
    """
    A container for managing a list of children for a given family.
    """

    def __init__(self, grstate, groptions, family):
        GrampsFrameGroupList.__init__(self, grstate, groptions)
        self.family = family

        context = "child"
        if "parent" in groptions.option_space:
            context = "sibling"

        child_number = 0
        for child_ref in self.family.get_child_ref_list():
            if child_ref:
                child = self.fetch("Person", child_ref.ref)
                groptions_copy = copy(groptions)
                groptions_copy.set_backlink(family.get_handle())
                groptions_copy.option_space = "options.group.{}".format(
                    context
                )
                child_number = child_number + 1
                if self.grstate.config.get(
                    "options.group.{}.number-children".format(context)
                ):
                    groptions_copy.set_number(child_number)
                profile = ChildGrampsFrame(
                    grstate,
                    groptions_copy,
                    child,
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
            for ref in self.family.get_child_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
                    break
        action = "{} {} {} {}".format(
            _("Reordered Children"),
            _("for"),
            _("Family"),
            self.family.get_gramps_id(),
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.family.set_child_ref_list(new_list)
            self.grstate.dbstate.db.commit_family(self.family, trans)

    def save_new_object(self, handle, insert_row):
        """
        Add a new child to the list of children.
        """
        if self.family.get_father_handle() == handle:
            return
        if self.family.get_mother_handle() == handle:
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
            for ref in self.family.get_child_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
        new_list.insert(insert_row, child_ref)
        child = self.fetch("Person", child_ref.ref)
        action = "{} {} {} {} {}".format(
            _("Added Child"),
            child.get_gramps_id(),
            _("to"),
            _("Family"),
            self.family.get_gramps_id(),
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.family.set_child_ref_list(new_list)
            self.grstate.dbstate.db.commit_family(self.family, trans)
            child.add_parent_family_handle(self.family.get_handle())
            self.grstate.dbstate.db.commit_person(child, trans)
