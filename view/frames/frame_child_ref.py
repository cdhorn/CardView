#
# Gramps - a GTK+/GNOME based genealogy program
#
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
ChildRefGrampsFrame
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
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditChildRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import menu_item
from .frame_person import PersonGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ChildRefGrampsFrame class
#
# ------------------------------------------------------------------------
class ChildRefGrampsFrame(PersonGrampsFrame):
    """
    The ChildRefGrampsFrame exposes some of the basic facts about a Child.
    """

    def __init__(
        self,
        grstate,
        groptions,
        family,
        child_ref,
    ):
        child = grstate.fetch("Person", child_ref.ref)
        PersonGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            child,
            reference_tuple=(family, child_ref),
        )
        if not groptions.ref_mode:
            return

        vbox = None
        if child_ref.get_father_relation():
            reltype = str(child_ref.get_father_relation())
            if groptions.ref_mode in [1, 3]:
                left = groptions.ref_mode == 1
                self.ref_widgets["body"].pack_start(
                    self.get_label(_("Father"), left=left), False, False, 0
                )
                self.ref_widgets["body"].pack_start(
                    self.get_label(str(reltype), left=left), False, False, 0
                )
            else:
                vbox = Gtk.VBox()
                vbox.pack_start(
                    self.get_label(": ".join((_("Father"), reltype))),
                    True,
                    True,
                    0,
                )

        if child_ref.get_mother_relation():
            reltype = str(child_ref.get_mother_relation())
            if groptions.ref_mode in [1, 3]:
                left = groptions.ref_mode == 1
                self.ref_widgets["body"].pack_start(
                    self.get_label(_("Mother"), left=left), False, False, 0
                )
                self.ref_widgets["body"].pack_start(
                    self.get_label(str(reltype), left=left), False, False, 0
                )
            else:
                if not vbox:
                    vbox = Gtk.VBox()
                vbox.pack_start(
                    self.get_label(": ".join((_("Mother"), reltype))),
                    True,
                    True,
                    0,
                )

        if vbox:
            self.ref_widgets["body"].pack_start(vbox, True, True, 0)

    def add_ref_custom_actions(self, context_menu):
        """
        Build the action menu for a right click on a reference object.
        """
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(menu_item("gtk-edit", label, self.edit_child_ref))
        label = " ".join((_("Delete"), _("reference")))
        context_menu.append(
            menu_item("list-remove", label, self.remove_family_child)
        )

    def edit_child_ref(self, *_dummy_obj):
        """
        Launch the editor.
        """
        try:
            name = name_displayer.display(self.primary.obj)
            EditChildRef(
                name,
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.reference.obj,
                self.save_ref,
            )
        except WindowActiveError:
            pass
