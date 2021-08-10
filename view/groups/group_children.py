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

from copy import copy

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn


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
        GrampsFrameGroupList.__init__(self, grstate, groptions, enable_drop=False)
        self.family = family

        context = "child"
        if "parent" in groptions.option_space:
            context = "sibling"

        child_number = 0
        for child_ref in self.family.get_child_ref_list():
            if child_ref:
                child = grstate.dbstate.db.get_person_from_handle(child_ref.ref)
                groptions_copy = copy(groptions)
                groptions_copy.set_backlink(family.get_handle())
                groptions_copy.option_space = "options.group.{}".format(context)
                child_number = child_number + 1
                if self.grstate.config.get("options.group.{}.number-children".format(context)):
                    groptions_copy.set_number(child_number)
                profile = ChildGrampsFrame(
                    grstate,
                    groptions_copy,
                    child,
                    child_ref,
                )
                self.add_frame(profile)
        self.show_all()

    def _save_child_list(self, new_list, comment):
        """
        Update and save child list.
        """
        with DbTxn(comment, self.grstate.dbstate.db) as trans:
            self.family.set_child_ref_list(new_list)
            self.grstate.dbstate.db.commit_family(self.family, trans)

    def save_reordered_list(self):
        """
        Save a reordered list of children.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.family.get_child_ref_list():
                if ref.ref == frame.obj.get_handle():
                    new_list.append(ref)
                    break
        action = "{} {} {} {}".format(
            _("Reordered Children"),
            _("for"),
            _("Family"),
            self.family.get_gramps_id(),
        )
        self._save_child_list(new_list, action)

    def save_new_object(self, handle, insert_row):
        """
        Add a new child to the list of children.
        """
        if self.family.get_father_handle() == handle:
            return
        if self.family.get_mother_handle() == handle:
            return
        new_list = []
        for frame in self.row_frames:
            new_list.append(frame.obj.get_handle())
        if handle in new_list:
            return
        new_list.insert(handle, insert_row)
        child = self.grstate.dbstate.db.get_person_from_handle(handle)
        action = "{} {} {} {} {}".format(
            _("Added Child"),
            child.get_gramps_id(),
            _("to"),
            _("Family"),
            self.family.get_gramps_id(),
        )
        self._save_child_list(new_list, action)
