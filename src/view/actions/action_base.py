#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2009       Benny Malengier
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
GrampsAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib.primaryobj import PrimaryObject
from gramps.gen.utils.string import data_recover_msg
from gramps.gui.dialog import QuestionDialog

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..common.common_utils import describe_object
from .action_const import GRAMPS_EDITORS
from .delete import delete_object

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsAction Class
#
# Arguments are used in two different manners based on the object type.
#
# When the object to perform the action on or for is a primary Gramps
# object then it is the action_object. An example would be a Note object.
# If the action involves another object then that is the target_object, and
# if it specifically modifies a child of that object then that is the
# target_child_object. Using Note as an example again, if removing a Note
# from a PersonRef then the Person is the target_object and the PersonRef
# is the target_child_object.
#
# When the object to perform the action on or for is a secondary Gramps
# object like a PersonRef itself then target_object is the parent object
# and the secondary object is the target_child_object.
#
# ------------------------------------------------------------------------
class GrampsAction:
    """
    Base class to support actions on or between Gramps objects.
    """

    def __init__(
        self,
        grstate,
        action_object=None,
        target_object=None,
        target_child_object=None,
    ):
        self.grstate = grstate
        self.action_object = self.__load_object(action_object)
        self.target_object = self.__load_object(target_object)
        self.target_child_object = self.__load_object(target_child_object)
        self.db = grstate.dbstate.db

    def __load_object(self, obj):
        """
        Return a Gramps object.
        """
        if isinstance(obj, GrampsObject):
            return obj
        return GrampsObject(obj)

    def set_action_object(self, action_object):
        """
        Set the action object.
        """
        self.action_object = self.__load_object(action_object)

    def set_target_object(self, target_object, target_child_object=None):
        """
        Set the target object to be modified.
        """
        self.target_object = self.__load_object(target_object)
        self.target_child_object = self.__load_object(target_child_object)

    def get_target_object(self):
        """
        Return target object to be modified.
        """
        if self.target_child_object:
            return self.target_child_object
        return self.target_object

    def describe_object(self, obj, gramps_id=True):
        """
        Return object description.
        """
        if not gramps_id or not isinstance(obj, PrimaryObject):
            return describe_object(self.db, obj)
        return "".join(
            (describe_object(self.db, obj), " [", obj.gramps_id, "]")
        )

    def verify_action(
        self, message1, message2, button, callback, recover_message=True
    ):
        """
        Verify an action with the user before performing it.
        """
        if recover_message:
            message2 = "%s %s" % (message2, data_recover_msg)
        QuestionDialog(
            message1,
            message2,
            button,
            callback,
            parent=self.grstate.uistate.window,
        )

    def edit_object(self, *_dummy_args):
        """
        Edit the object.
        """
        if (
            self.action_object.is_primary
            or self.action_object.obj_type == "Tag"
        ):
            try:
                GRAMPS_EDITORS[self.action_object.obj_type](
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.action_object.obj,
                )
            except WindowActiveError:
                pass
        elif not self.action_object.is_reference:
            try:
                GRAMPS_EDITORS[self.action_object.obj_type](
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.action_object.obj,
                    self._edited_object,
                )
            except WindowActiveError:
                pass

    def _edited_object(self, obj):
        """
        Save the edited object.
        """
        if not obj:
            return
        message = " ".join(
            (
                _("Edited"),
                self.action_object.obj_lang,
                _("for"),
                self.target_object.obj_lang,
                self.target_object.obj.gramps_id,
            )
        )
        self.target_object.commit(self.grstate, message)

    def delete_object(self, _dummy_arg, override_object=None, *_dummy_args):
        """
        Start the object deletion process.
        """
        if override_object:
            target_object = override_object
        else:
            target_object = self.action_object
        if target_object and (
            target_object.is_primary or target_object.obj_type == "Tag"
        ):
            backlink_count = len(
                list(
                    self.grstate.dbstate.db.find_backlink_handles(
                        target_object.obj.handle
                    )
                )
            )
            obj_lang = target_object.obj_lang
            message1 = _("Delete %s %s?") % (
                obj_lang,
                self.describe_object(target_object.obj),
            )
            message2 = _(
                "Deleting the %s will remove the %s from the database."
            ) % (obj_lang.lower(), obj_lang.lower())
            if backlink_count > 0:
                message2 = "%s %s" % (
                    message2,
                    _(
                        "Any references by other objects with additional data "
                        "they may contain will also be removed"
                    ),
                )
                if backlink_count > 1:
                    message2 = "%s %s" % (
                        message2,
                        _(
                            "and %s other objects in the database still refer "
                            "to this one."
                        )
                        % str(backlink_count),
                    )
                else:
                    message2 = "%s %s" % (
                        message2,
                        _(
                            "and 1 other object in the database still refers "
                            "to this one."
                        ),
                    )
            else:
                message2 = "%s %s" % (
                    message2,
                    _("No other objects in the database refer to this one."),
                )
            callback = lambda: self._delete_object(target_object)
            self.verify_action(
                message1, message2, _("Delete %s") % obj_lang, callback
            )

    def _delete_object(self, override_object=None, *_dummy_args):
        """
        Perform the actual delete.
        """
        if override_object:
            target_object = override_object
        else:
            target_object = self.action_object
        self.grstate.uistate.set_busy_cursor(True)
        text = self.describe_object(target_object.obj)
        delete_object(
            self.db,
            target_object.obj.handle,
            target_object.obj_type,
            _("Deleted %s") % text,
        )
        self.grstate.uistate.set_busy_cursor(False)

    def pivot_focus(self, obj, obj_type):
        """
        Move active focus to a newly added object.
        """
        self.grstate.load_primary_page(obj_type, obj)
