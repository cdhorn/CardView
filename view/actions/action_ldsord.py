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
LdsOrdAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import LdsOrd
from gramps.gui.editors import EditLdsOrd, EditFamilyLdsOrd

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# LdsOrdAction class
#
# ------------------------------------------------------------------------
class LdsOrdAction(GrampsAction):
    """
    Class to support actions related to the LDS ordinances of a person.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)

    def _edit_ordinance(self, ordinance, callback=None):
        """
        Add a new ordinance.
        """
        if self.target_object.obj_type == "Family":
            editor = EditFamilyLdsOrd
        else:
            editor = EditLdsOrd
        try:
            editor(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                ordinance,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_object(self, *_dummy_args):
        """
        Edit an ordinance. This overrides default method.
        """
        callback = lambda x: self._edited_ordinance(
            x, self.action_object.obj_hash
        )
        self._edit_ordinance(self.action_object.obj, callback)

    def _edited_ordinance(self, ordinance, old_hash):
        """
        Save edited ordinance.
        """
        if ordinance:
            self.grstate.update_history_object(old_hash, ordinance)
            message = _("Edited Ordinance %s for %s") % (
                ordinance.type2str(),
                self.describe_object(self.target_object.obj),
            )
            self.target_object.commit(self.grstate, message)

    def add_ordinance(self, *_dummy_args):
        """
        Add a new ordinance.
        """
        self._edit_ordinance(LdsOrd(), self._added_ordinance)

    def _added_ordinance(self, ordinance):
        """
        Save the new name to finish adding it.
        """
        if ordinance:
            message = _("Added Ordinance %s to %s") % (
                ordinance.type2str(),
                self.describe_object(self.target_object.obj),
            )
            self.target_object.obj.add_lds_ord(ordinance)
            self.target_object.commit(self.grstate, message)

    def delete_object(self, *_dummy_args):
        """
        Delete the ordinance. This overrides default method.
        """
        if self.action_object:
            ordinance_type = self.action_object.obj.type2str()
            message1 = _("Delete Ordinance %s?") % ordinance_type
            message2 = _(
                "Deleting the ordinance will remove the ordinance from "
                "the %s %s in the database."
            ) % (
                self.target_object.obj_lang.lower(),
                self.describe_object(self.target_object.obj),
            )
            self.verify_action(
                message1,
                message2,
                _("Delete %s") % ordinance_type,
                self._delete_object,
            )

    def _delete_object(self, *_dummy_args):
        """
        Actually delete the ordinance.
        """
        message = _("Deleted Ordinance %s from %s") % (
            self.action_object.obj.type2str(),
            self.describe_object(self.target_object.obj),
        )
        self.target_object.obj.remove_lds_ord(self.action_object.obj)
        self.target_object.commit(self.grstate, message)


factory.register_action("LdsOrd", LdsOrdAction)
