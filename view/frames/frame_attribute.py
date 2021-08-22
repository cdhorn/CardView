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
AttributeGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from html import escape


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
from gramps.gen.utils.alive import probably_alive
from gramps.gui.display import display_url

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_const import _LEFT_BUTTON, _RIGHT_BUTTON
from .frame_secondary import SecondaryGrampsFrame
from .frame_utils import button_activated, get_person_color_css, TextLink

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AttributeGrampsFrame class
#
# ------------------------------------------------------------------------
class AttributeGrampsFrame(SecondaryGrampsFrame):
    """
    The AttributeGrampsFrame exposes facts about an Attribute.
    """

    def __init__(
        self,
        grstate,
        groptions,
        obj,
        attribute,
    ):
        SecondaryGrampsFrame.__init__(self, grstate, groptions, obj, attribute)

        name = glocale.translation.sgettext(attribute.get_type().xml_str())
        label = TextLink(
            name,
            self.primary.obj_type,
            self.primary.obj.get_handle(),
            self.switch_attribute_page,
        )
        self.title.pack_start(label, False, False, 0)

        if attribute.get_value():
            self.add_fact(self.make_label(attribute.get_value()))

        self.show_all()
        self.enable_drag()
        self.set_css_style()

    def switch_attribute_page(self, *_dummy_obj):
        """
        Initiate switch to attribute page.
        """
        self.switch_object(None, None, "Attribute", self.secondary.obj)

    def edit_secondary_object(self, _dummy_var1=None):
        """
        Override default method to launch the attribute editor.
        """
        self.edit_attribute(None, self.secondary.obj)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("options.global.use-color-scheme"):
            return ""

        if self.primary.obj_type == "Person":
            living = probably_alive(self.primary.obj, self.grstate.dbstate.db)
            return get_person_color_css(
                self.primary.obj,
                living=living,
            )
        return ""
