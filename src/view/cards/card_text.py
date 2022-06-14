#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022       Christopher Horn
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
TextCard
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
from html import escape

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

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .card_generic import GenericCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TextCard Class
#
# ------------------------------------------------------------------------
class TextCard(GenericCard):
    """
    The TextCard class is pushed data to display.
    """

    def __init__(self, grstate, groptions, title=None, data=None):
        GenericCard.__init__(self, grstate, groptions, None)
        self.title = title
        self.data = data
        self.build_layout()
        self.load_layout()
        self.set_css_style()

    def load_layout(self):
        """
        Load the layout.
        """
        widgets = self.widgets
        if self.title:
            label = Gtk.Label(
                use_markup=True,
                label=self.title_markup.format(
                    "<b>%s</b>" % escape(self.title)
                ),
            )
            widgets["title"].pack_start(label, False, False, 0)

        facts = self.widgets["facts"]
        for (label, value) in self.data:
            facts.add_fact(
                self.get_label(str(value)), label=self.get_label(label)
            )

    def build_layout(self):
        """
        Construct basic card layout.
        """
        widgets = self.widgets
        fact_block = Gtk.VBox()
        widgets["body"].pack_start(
            fact_block, expand=True, fill=True, padding=0
        )
        fact_block.pack_start(
            widgets["title"], expand=True, fill=True, padding=0
        )
        fact_block.pack_start(
            widgets["facts"], expand=True, fill=True, padding=0
        )

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("display.border-width")
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
