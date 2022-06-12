#
# Gramps - a GTK+/GNOME based genealogy program
#
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
AttributeCard
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
from ..common.common_classes import GrampsContext
from .card_secondary import SecondaryCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AttributeCard Class
#
# ------------------------------------------------------------------------
class AttributeCard(SecondaryCard):
    """
    The AttributeCard exposes facts about an Attribute.
    """

    def __init__(self, grstate, groptions, obj, attribute):
        SecondaryCard.__init__(self, grstate, groptions, obj, attribute)
        self.__add_attribute_title(attribute)
        self.__add_attribute_value(attribute)
        self.enable_drag()
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_attribute_title(self, attribute):
        """
        Add attribute title.
        """
        name = glocale.translation.sgettext(attribute.get_type().xml_str())
        if "Ref" not in self.primary.obj_type:
            label = self.get_link(
                name,
                self.primary.obj_type,
                self.primary.obj.handle,
                callback=self.switch_attribute_page,
            )
        else:
            name = "<b>%s</b>" % escape(name)
            label = Gtk.Label(
                halign=Gtk.Align.START,
                wrap=True,
                xalign=0.0,
                justify=Gtk.Justification.LEFT,
            )
            label.set_markup(name)
        self.widgets["title"].pack_start(label, False, False, 0)

    def __add_attribute_value(self, attribute):
        """
        Add attribute value.
        """
        if attribute.get_value():
            self.add_fact(self.get_label(attribute.get_value()))

    def switch_attribute_page(self, *_dummy_obj):
        """
        Initiate switch to attribute page.
        """
        context = GrampsContext(self.primary.obj, None, self.secondary.obj)
        self.grstate.load_page(context.pickled)

    def route_action(self, obj, event):
        """
        Route the action if the card was clicked on.
        """
        if "Ref" not in self.primary.obj_type:
            SecondaryCard.route_action(self, obj, event)
