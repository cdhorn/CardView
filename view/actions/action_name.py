#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
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
NameAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Name
from gramps.gui.editors import EditName

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# NameAction class
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
        self.grstate.update_history_object(old_hash, name)
        message = self.commit_message(
            _("Name"), name.get_regular_name(), action="update"
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
            message = " ".join(
                (
                    _("Added"),
                    _("Name"),
                    name.get_regular_name(),
                    _("to"),
                    self.target_object.obj_lang,
                    self.target_object.obj.get_gramps_id(),
                )
            )
            self.target_object.obj.add_alternate_name(name)
            self.target_object.commit(self.grstate, message)

    def remove_name(self, *_dummy_args):
        """
        Remove the given name from the current object.
        """
        if not self.action_object:
            return
        text = self.action_object.obj.get_regular_name()
        prefix = _(
            "You are about to remove the following name from this object:"
        )
        if self.confirm_action(_("Warning"), prefix, "\n\n<b>", text, "</b>"):
            message = " ".join(
                (
                    _("Deleted"),
                    _("Name"),
                    text,
                    _("from"),
                    self.target_object.obj_lang,
                    self.target_object.obj.get_gramps_id(),
                )
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
