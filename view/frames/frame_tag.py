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
TagFrame
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

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from .frame_base import GrampsFrame
from ..menus.menu_utils import menu_item, new_menu, show_menu


_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TagFrame class
#
# ------------------------------------------------------------------------
class TagFrame(GrampsFrame):
    """
    The TagFrame class exposes information about a tag.
    """

    def __init__(self, grstate, groptions, tag):
        GrampsFrame.__init__(self, grstate, groptions, tag)

        fact_block = Gtk.VBox()
        self.widgets["body"].pack_start(
            fact_block, expand=True, fill=True, padding=0
        )
        fact_block.pack_start(
            self.widgets["title"], expand=True, fill=True, padding=0
        )
        fact_block.pack_start(
            self.widgets["facts"], expand=True, fill=True, padding=0
        )

        image = Gtk.Image()
        image.set_from_icon_name("gramps-tag", Gtk.IconSize.BUTTON)
        self.widgets["title"].set_spacing(6)
        self.widgets["title"].pack_start(image, False, False, 0)

        css = "".join(
            (
                ".image { margin: 0px; padding: 0px; background-image: none; ",
                "background-color: ",
                tag.color[:7],
                "; }",
            )
        )
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = image.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("image")

        label = Gtk.Label(
            use_markup=True, label="".join(("<b>", tag.name, "</b>"))
        )
        self.widgets["title"].pack_start(label, False, False, 0)

        self.widgets["facts"].attach(self.get_label(_("Priority")), 0, 0, 1, 1)
        self.widgets["facts"].attach(
            self.get_label(str(tag.priority)), 1, 0, 1, 1
        )
        self.widgets["facts"].attach(self.get_label(_("Color")), 0, 1, 1, 1)
        label = self.get_label(tag.color)
        self.widgets["facts"].attach(label, 1, 1, 1, 1)
        self.set_css_style()

    def build_context_menu(self, _dummy_obj, event):
        """
        Build the action menu for the tag.
        """
        action = action_handler("Tag", self.grstate, self.primary)
        menu = new_menu("gramps-tag", _("Edit tag"), action.edit_tag)
        menu.add(
            menu_item("gramps-tag", _("Organize tags"), action.organize_tags)
        )
        return show_menu(menu, self, event)

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("options.global.display.border-width")
        color = self.get_color_css()
        css = "".join(
            (".frame { border-width: ", str(border), "px; ", color, " }")
        )
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
