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
AttributeAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Attribute, SrcAttribute
from gramps.gui.editors import EditAttribute, EditSrcAttribute

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from ..config.config_selectors import get_attribute_types

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AttributeAction class
#
# action_object is the Attribute when applicable
# target_object and target_child_object are AttributeBase objects
# Handles SrcAttribute and SrcAttributeBase as well
#
# ------------------------------------------------------------------------
class AttributeAction(GrampsAction):
    """
    Class to support actions on or with attribute objects.
    """

    def __init__(
        self,
        grstate,
        action_object=None,
        target_object=None,
        target_child_object=None,
    ):
        GrampsAction.__init__(
            self, grstate, action_object, target_object, target_child_object
        )

    def _edit_attribute(self, attribute, attribute_types, callback):
        """
        Launch attribute editor.
        """
        if isinstance(attribute, SrcAttribute):
            editor = EditSrcAttribute
        else:
            editor = EditAttribute
        try:
            editor(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                attribute,
                "",
                attribute_types,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_attribute(self, *_dummy_args):
        """
        Edit an attribute.
        """
        attribute_types = get_attribute_types(
            self.db, self.target_object.obj_type
        )
        callback = lambda x: self._edited_attribute(
            x, self.action_object.obj_hash
        )
        self._edit_attribute(self.action_object.obj, attribute_types, callback)

    def _edited_attribute(self, attribute, old_hash):
        """
        Save edited attribute.
        """
        if attribute:
            self.grstate.update_history_object(old_hash, attribute)
            message = self.commit_message(
                _("Attribute"), attribute.get_type(), action="update"
            )
            self.target_object.commit(self.grstate, message)

    def add_attribute(self, *_dummy_args):
        """
        Add a new attribute.
        """
        active_target_object = self.get_target_object()
        attribute_types = get_attribute_types(
            self.db, self.target_object.obj_type
        )
        if active_target_object.obj_type in ["Source", "Citation"]:
            attribute = SrcAttribute()
        else:
            attribute = Attribute()
        self._edit_attribute(attribute, attribute_types, self._added_attribute)

    def _added_attribute(self, attribute):
        """
        Save the new attribute to finish adding it.
        """
        if attribute:
            active_target_object = self.get_target_object()
            message = self.commit_message(
                _("Attribute"), str(attribute.get_type())
            )
            active_target_object.obj.add_attribute(attribute)
            self.target_object.commit(self.grstate, message)

    def remove_attribute(self, *_dummy_args):
        """
        Remove the given attribute from the current object.
        """
        if not self.action_object:
            return
        active_target_object = self.get_target_object()
        text = self.describe_object(self.action_object.obj)
        prefix = _(
            "You are about to remove the following attribute from this object:"
        )
        if self.confirm_action(_("Warning"), prefix, "\n\n<b>", text, "</b>"):
            message = self.commit_message(
                _("Attribute"),
                str(self.action_object.obj.get_type()),
                action="remove",
            )
            active_target_object.obj.remove_attribute(self.action_object.obj)
            self.target_object.commit(self.grstate, message)
