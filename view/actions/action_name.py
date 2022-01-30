#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
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
NameAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Name
from gramps.gui.editors import EditName

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
# NameAction Class
#
# action_object is the Name when applicable
# target_object is the Person object
#
# ------------------------------------------------------------------------
class NameAction(GrampsAction):
    """
    Class to support actions related to the names of a person.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)

    def _edit_name(self, name, callback):
        """
        Launch name editor.
        """
        try:
            EditName(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                name,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_name(self, *_dummy_args):
        """
        Edit a name.
        """
        callback = lambda x: self._edited_name(x, self.action_object.obj_hash)
        self._edit_name(self.action_object.obj, callback)

    def _edited_name(self, name, old_hash):
        """
        Save edited name.
        """
        if name:
            self.grstate.update_history_object(old_hash, name)
            message = _("Edited Name %s for %s") % (
                name.get_regular_name(),
                self.describe_object(self.target_object.obj),
            )
            self.target_object.commit(self.grstate, message)

    def add_name(self, *_dummy_args):
        """
        Add a new name.
        """
        self._edit_name(Name(), self._added_name)

    def _added_name(self, name):
        """
        Save the new name to finish adding it.
        """
        if name:
            message = _("Added Name %s to %s") % (
                name.get_regular_name(),
                self.describe_object(self.target_object.obj),
            )
            self.target_object.obj.add_alternate_name(name)
            self.target_object.commit(self.grstate, message)

    def delete_object(self, *_dummy_args):
        """
        Delete the given name. This overrides default method.
        """
        if self.action_object:
            name = self.action_object.obj.get_regular_name()
            message1 = _("Delete Name %s?") % name
            message2 = _(
                "Deleting the name will remove the name from "
                "the %s %s in the database."
            ) % (
                self.target_object.obj_lang.lower(),
                self.describe_object(self.target_object.obj),
            )
            self.verify_action(
                message1,
                message2,
                _("Delete Name"),
                self._delete_object,
            )

    def _delete_object(self, *_dummy_args):
        """
        Actually delete the name.
        """
        message = _("Deleted Name %s from %s") % (
            self.action_object.obj.get_regular_name(),
            self.describe_object(self.target_object.obj),
        )
        name_list = []
        for alternate_name in self.target_object.obj.get_alternate_names():
            if (
                alternate_name.serialize()
                != self.action_object.obj.serialize()
            ):
                name_list.append(alternate_name)
        self.target_object.obj.set_alternate_names(name_list)
        self.target_object.commit(self.grstate, message)


factory.register_action("Name", NameAction)
