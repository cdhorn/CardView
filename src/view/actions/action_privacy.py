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
PrivacyAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib.privacybase import PrivacyBase

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
# PrivacyAction Class
#
# target_object and target_child_object are PrivacyBase objects
#
# ------------------------------------------------------------------------
class PrivacyAction(GrampsAction):
    """
    Class to support toggling the privacy option on an object.
    """

    def __init__(self, grstate, target_object, target_child_object=None):
        GrampsAction.__init__(
            self,
            grstate,
            target_object=target_object,
            target_child_object=target_child_object,
        )

    def is_valid(self):
        """
        Return true if had privacy attribute.
        """
        active_target_object = self.get_target_object()
        return isinstance(active_target_object.obj, PrivacyBase)

    def is_set(self):
        """
        Return true if set.
        """
        active_target_object = self.get_target_object()
        return active_target_object.obj.private

    def toggle(self, *_dummy_args):
        """
        Toggle the privacy indicator.
        """
        active_target_object = self.get_target_object()
        mode = active_target_object.obj.private
        if mode:
            text = _("Public")
        else:
            text = _("Private")
        if self.target_child_object:
            message = _("Made %s for %s %s") % (
                self.target_child_object.obj_lang,
                self.describe_object(self.target_object.obj),
                text,
            )
        else:
            message = _("Made %s %s") % (
                self.describe_object(self.target_object.obj),
                text,
            )
        active_target_object.save_hash()
        active_target_object.obj.set_privacy(not mode)
        active_target_object.sync_hash(self.grstate)
        self.target_object.commit(self.grstate, message)


factory.register_action("Privacy", PrivacyAction)
