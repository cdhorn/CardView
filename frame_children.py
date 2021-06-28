#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
ChildrenGrampsFrameGroup
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
from gramps.gen.db import DbTxn


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsConfig
from frame_list import GrampsFrameList
from frame_person import PersonGrampsFrame


# ------------------------------------------------------------------------
#
# Internationalisation
#
# ------------------------------------------------------------------------
try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# ChildrenGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class ChildrenGrampsFrameGroup(GrampsFrameList):
    def __init__(
        self,
        dbstate,
        uistate,
        family,
        context,
        space,
        config,
        router,
        parent=None,
        relation=None,
        children="Children",
        defaults=None,
    ):
        GrampsFrameList.__init__(self, dbstate, uistate, space, config)
        self.family = family
        self.context = context
        self.parent = parent
        self.relation = relation
        self.router = router
        self.children = children
        self.number = 0

        context = "child"
        if self.context == "parent":
            context = "sibling"

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        for ref in self.family.get_child_ref_list():
            if ref:
                child = self.dbstate.db.get_person_from_handle(ref.ref)
                child_number = self.number + 1
                if not self.option(context, "number-children"):
                    child_number = 0
                profile = PersonGrampsFrame(
                    self.dbstate,
                    self.uistate,
                    child,
                    context,
                    self.space,
                    self.config,
                    self.router,
                    number=child_number,
                    relation=self.relation,
                    groups=groups,
                    defaults=defaults,
                    family_backlink=family.handle
                )
                self.add_frame(profile)
                self.number = self.number + 1
        self.show_all()

    def save_reordered_list(self):
        """
        Save a reordered list of children.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.family.get_child_ref_list():
                if ref.ref == frame.obj.get_handle():
                    new_list.append(ref)
                    break

        with DbTxn(_("Save reordered child list"), self.dbstate.db) as trans:
            self.family.set_child_ref_list(new_list)
            self.dbstate.db.commit_family(self.family, trans)

