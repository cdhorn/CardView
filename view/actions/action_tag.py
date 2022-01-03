#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2021       Christopher Horn
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
TagAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Tag
from gramps.gui.views.tags import EditTag, OrganizeTagsDialog

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TagAction class
#
# action_object is the Tag when applicable
# target_object is the TagBase object
#
# ------------------------------------------------------------------------
class TagAction(GrampsAction):
    """
    Class to support actions on or with tag objects.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)

    def new_tag(self, *_dummy_args):
        """
        Create a new tag.
        """
        try:
            EditTag(self.db, self.grstate.uistate, [], Tag())
        except WindowActiveError:
            pass

    def organize_tags(self, *_dummy_args):
        """
        Organize tags.
        """
        try:
            OrganizeTagsDialog(self.db, self.grstate.uistate, [])
        except WindowActiveError:
            pass

    def add_tag(self, *_dummy_args):
        """
        Add the given tag to the current object.
        """
        if not self.action_object:
            return
        message = self.commit_message(
            _("Tag"), self.action_object.obj.get_name()
        )
        self.target_object.obj.add_tag(self.action_object.obj.get_handle())
        self.target_object.commit(self.grstate, message)

    def remove_tag(self, *_dummy_args):
        """
        Remove the given tag from the current object.
        """
        if not self.action_object:
            return
        message = self.commit_message(
            _("Tag"), self.action_object.obj.get_name(), action="remove"
        )
        if self.target_object.obj.remove_tag(
            self.action_object.obj.get_handle()
        ):
            self.target_object.commit(self.grstate, message)
