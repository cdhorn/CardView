#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
TagAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Tag
from gramps.gui.views.tags import EditTag, OrganizeTagsDialog

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TagAction Class
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

    def edit_tag(self, *_dummy_args):
        """
        Edit a tag.
        """
        try:
            EditTag(self.db, self.grstate.uistate, [], self.action_object.obj)
        except WindowActiveError:
            pass

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
        message = _("Added Tag %s to %s %s") % (
            self.action_object.obj.get_name(),
            self.target_object.obj_lang,
            self.describe_object(self.target_object.obj),
        )
        self.target_object.obj.add_tag(self.action_object.obj.get_handle())
        self.target_object.commit(self.grstate, message)

    def add_new_tag(self, *_dummy_args):
        """
        Create a new tag and add to current object.
        """
        self.set_action_object(Tag())
        try:
            EditTagWrapper(
                self.db,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                callback=self.add_tag,
            )
        except WindowActiveError:
            pass

    def remove_tag(self, *_dummy_args):
        """
        Remove the given tag from the current object.
        """
        if not self.action_object:
            return
        message = _("Removed Tag %s from %s %s") % (
            self.action_object.obj.get_name(),
            self.target_object.obj_lang,
            self.describe_object(self.target_object.obj),
        )
        if self.target_object.obj.remove_tag(
            self.action_object.obj.get_handle()
        ):
            self.target_object.commit(self.grstate, message)


class EditTagWrapper(EditTag):
    """
    A class to wrap the tag editor to provide callback support.
    """

    def __init__(self, db, uistate, track, tag, callback=None):
        self.callback = callback
        self.saved = False
        EditTag.__init__(self, db, uistate, track, tag)

    def _save(self):
        """
        Handle save and set saved flag.
        """
        EditTag._save(self)
        self.saved = True

    def run(self):
        """
        Run the dialog and if user saved execute callback.
        """
        EditTag.run(self)
        if self.saved and self.callback:
            self.callback(self.tag)


factory.register_action("Tag", TagAction)
