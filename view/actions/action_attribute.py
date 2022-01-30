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
AttributeAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Attribute, SrcAttribute
from gramps.gui.editors import EditAttribute, EditSrcAttribute

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..config.config_selectors import get_attribute_types
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AttributeAction Class
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
            active_target_object = self.get_target_object()
            message = _("Edited Attribute %s for %s") % (
                attribute.get_type(),
                self.describe_object(active_target_object.obj),
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
            message = _("Added Attribute %s to %s") % (
                attribute.get_type(),
                self.describe_object(active_target_object.obj),
            )
            active_target_object.obj.add_attribute(attribute)
            self.target_object.commit(self.grstate, message)

    def delete_object(self, *_dummy_args):
        """
        Delete the attribute. This overrides the default method.
        """
        if not self.action_object:
            return
        active_target_object = self.get_target_object()
        target_name = self.describe_object(active_target_object.obj)
        attribute_type = str(self.action_object.obj.get_type())
        message1 = _("Delete Attribute %s?") % attribute_type
        message2 = _(
            "Deleting the attribute will remove the attribute from "
            "the %s %s in the database."
        ) % (active_target_object.obj_lang.lower(), target_name)
        self.verify_action(
            message1,
            message2,
            _("Delete %s") % attribute_type,
            self._delete_object,
        )

    def _delete_object(self, *_dummy_args):
        """
        Actually delete the attribute.
        """
        active_target_object = self.get_target_object()
        message = _("Deleted Attribute %s from %s") % (
            self.action_object.obj.get_type(),
            self.describe_object(active_target_object.obj),
        )
        active_target_object.obj.remove_attribute(self.action_object.obj)
        self.target_object.commit(self.grstate, message)

    def edit_object(self, *_dummy_args):
        """
        Edit the attribute. This overrides default method.
        """
        self.edit_attribute()


factory.register_action("Attribute", AttributeAction)
