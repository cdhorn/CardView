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
GrampsAction
"""

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
from gramps.gen.errors import WindowActiveError

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..common.common_const import GRAMPS_EDITORS
from ..common.common_utils import describe_object

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsAction class
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

    def describe_object(self, obj):
        """
        Return object description.
        """
        return describe_object(self.db, obj)

    def confirm_action(self, title, *args):
        """
        If enabled display message and confirm a user requested action.
        """
        if not self.grstate.config.get(
            "options.global.general.enable-warnings"
        ):
            return True
        dialog = Gtk.Dialog(parent=self.grstate.uistate.window)
        dialog.set_title(title)
        dialog.set_default_size(500, 300)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)

        label = Gtk.Label(
            hexpand=True,
            vexpand=True,
            halign=Gtk.Align.CENTER,
            justify=Gtk.Justification.CENTER,
            use_markup=True,
            wrap=True,
            label="".join(
                args + ("\n\n", _("Are you sure you want to continue?"))
            ),
        )
        dialog.vbox.add(label)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        return False

    def commit_message(self, obj_type, obj_label, action="add"):
        """
        Construct a commit message string.
        """
        if action == "add":
            action = _("Added")
            preposition = _("to")
        elif action == "remove":
            action = _("Removed")
            preposition = _("from")
        else:
            action = _("Updated")
            preposition = _("for")

        if self.target_child_object:
            return " ".join(
                (
                    action,
                    obj_type,
                    obj_label,
                    preposition,
                    self.target_child_object.obj_lang,
                    _("for"),
                    self.target_object.obj_lang,
                    self.target_object.obj.get_gramps_id(),
                )
            )
        return " ".join(
            (
                action,
                obj_type,
                obj_label,
                preposition,
                self.target_object.obj_lang,
                self.target_object.obj.get_gramps_id(),
            )
        )

    def edit_object(self, *_dummy_args):
        """
        Edit the object.
        """
        if self.action_object.is_primary:
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
                self.target_object.obj.get_gramps_id(),
            )
        )
        self.target_object.commit(self.grstate, message)
