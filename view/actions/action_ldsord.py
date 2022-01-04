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

    def add_ordinance(self, *_dummy_args):
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
                LdsOrd(),
                self._added_ordinance,
            )
        except WindowActiveError:
            pass

    def _added_ordinance(self, ordinance):
        """
        Save the new name to finish adding it.
        """
        if ordinance:
            message = " ".join(
                (
                    _("Added"),
                    _("Ordinance"),
                    ordinance.type2str(),
                    _("to"),
                    self.target_object.obj_lang,
                    self.target_object.obj.get_gramps_id(),
                )
            )
            self.target_object.obj.add_lds_ord(ordinance)
            self.target_object.commit(self.grstate, message)

    def delete_object(self, *_dummy_args):
        """
        Delete the ordinance. This overrides default method.
        """
        if not self.action_object:
            return
        ordinance = self.action_object.obj
        text = ordinance.type2str()
        ordinance_date = ordinance.get_date_object()
        if ordinance_date:
            date = glocale.date_displayer.display(ordinance_date)
            if date:
                text = "".join((date, ": ", text))
        prefix = _(
            "You are about to delete the following ordinance from this object:"
        )
        if self.confirm_action(_("Warning"), prefix, "\n\n<b>", text, "</b>"):
            message = " ".join(
                (
                    _("Deleted"),
                    _("Ordinance"),
                    text,
                    _("from"),
                    self.target_object.obj_lang,
                    self.target_object.obj.get_gramps_id(),
                )
            )
            self.target_object.obj.remove_lds_ord(ordinance)
            self.target_object.commit(self.grstate, message)


factory.register_action("LdsOrd", LdsOrdAction)
