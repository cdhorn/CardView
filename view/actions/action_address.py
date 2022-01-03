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
AddressAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditAddress

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AddressAction class
#
# ------------------------------------------------------------------------
class AddressAction(GrampsAction):
    """
    Class to support actions related to address objects.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, action_object, target_object)

    def edit_address(self, *_dummy_args):
        """
        Edit an address.
        """
        callback = lambda x: self._edited_address(
            x, self.action_object.obj_hash
        )
        try:
            EditAddress(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                callback,
            )
        except WindowActiveError:
            pass

    def _edited_address(self, address, old_hash):
        """
        Save edited address.
        """
        self.grstate.update_history_object(old_hash, address)
        message = " ".join(
            (
                _("Edited"),
                _("Address"),
                _("for"),
                self.target_object.obj_lang,
                self.target_object.obj.get_gramps_id(),
            )
        )
        self.target_object.commit(self.grstate, message)
