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
GrampsFrameGroup helper classes
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

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsFrameGroupExpander class
#
# ------------------------------------------------------------------------
class GrampsFrameGroupExpander(Gtk.Expander):
    """
    A simple class for managing collapse of a GrampsFrameGroup object.
    """

    def __init__(self, grstate, groptions, expanded=True, use_markup=True):
        Gtk.Expander.__init__(
            self, expanded=expanded, use_markup=use_markup, hexpand=True
        )
        self.set_resize_toplevel(True)
        self.grstate = grstate
        self.hideable = grstate.config.get(
            "options.page.{}.layout.{}.hideable".format(
                grstate.page_type, groptions.context
            )
        )
        self.tabbed = grstate.config.get(
            "options.page.{}.layout.tabbed".format(grstate.page_type)
        )
        self.scrolled = grstate.config.get(
            "options.page.{}.layout.scrolled".format(grstate.page_type)
        )
        self.connect("activate", self.collapse)

    def collapse(self, _dummy_obj):
        """
        Handle removing the frame on collapse if needed.
        """
        if not self.tabbed:
            if self.get_expanded() and self.hideable:
                child = self.get_child()
                list(map(child.remove, child.get_children()))
                parent = self.get_parent()
                if not self.scrolled:
                    parent.remove(self)
                else:
                    gparent = parent.get_parent()
                    ggparent = gparent.get_parent()
                    gggparent = ggparent.get_parent()
                    parent.remove(self)
                    gparent.remove(parent)
                    ggparent.remove(gparent)
                    gggparent.remove(ggparent)
