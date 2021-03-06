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
CardGroup helper classes
"""

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.utils import match_primary_mask

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_const import BUTTON_SECONDARY
from ..common.common_utils import button_pressed

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CardGroupExpander Class
#
# ------------------------------------------------------------------------
class CardGroupExpander(Gtk.Expander):
    """
    A simple class for managing collapse of a CardGroup object.
    """

    def __init__(
        self, grstate, hide_title=True, expanded=True, use_markup=True
    ):
        Gtk.Expander.__init__(
            self, expanded=expanded, use_markup=use_markup, hexpand=True
        )
        self.set_resize_toplevel(False)
        self.connect("button-press-event", self.button_press)
        self.connect("activate", self.toggle_state)

        self.grstate = grstate
        self.hidden = False
        self.nested = None
        self.hidden_title = hide_title

    def button_press(self, _dummy_obj, event):
        """
        Handle button press.
        """
        if button_pressed(event, BUTTON_SECONDARY) and match_primary_mask(
            event.state
        ):
            self.hide()
            self.grstate.set_dirty_redraw_trigger()
            return True
        return False

    def toggle_state(self, _dummy_obj):
        """
        Expand or collapse as needed.
        """
        if self.hidden:
            self.set_hexpand(True)
            self.show_all()
            self.hidden = False
        elif self.get_expanded():
            if self.hidden_title:
                parent = self.get_parent()
                gparent = parent.get_parent()
                ggparent = gparent.get_parent()
                if not hasattr(ggparent, "nested"):
                    self.set_hexpand(False)
                    for child in self.get_children():
                        child.hide()
                    self.hidden = True
        return True
