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
CardView class for managing the card widgets and layout.
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

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsConfig
from .card_widgets import CardGrid, CardIcons

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CardView class
#
# ------------------------------------------------------------------------
class CardView(Gtk.VBox, GrampsConfig):
    """
    A simple class to encapsulate the widget layout for a Gramps card.
    """

    def __init__(self, grstate, groptions):
        Gtk.VBox.__init__(self, hexpand=True, vexpand=False)
        GrampsConfig.__init__(self, grstate, groptions)
        self.frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        self.widgets = {
            "body": Gtk.HBox(vexpand=False, hexpand=True, margin=3)
        }
        self.eventbox = Gtk.EventBox()

        self.ref_frame = None
        self.ref_widgets = {}
        self.ref_eventbox = None

    def init_layout(self):
        """
        Initialize the default card layout.
        """
        self._init_widgets()
        if self.groptions.ref_mode:
            self._prepare_ref_layout()
        else:
            self._prepare_normal_layout()

    def _init_widgets(self):
        """
        Initialize primary card widgets.
        """
        widgets = self.widgets

        widgets["image"] = Gtk.VBox(valign=Gtk.Align.START)
        widgets["age"] = Gtk.VBox(
            margin_right=3,
            margin_left=3,
            margin_top=3,
            margin_bottom=3,
            spacing=2,
        )
        widgets["title"] = Gtk.HBox(
            hexpand=True,
            vexpand=False,
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
        )
        widgets["facts"] = CardGrid()
        if "active" in self.groptions.option_space:
            widgets["extra"] = CardGrid()
        widgets["icons"] = CardIcons(self.grstate, self.groptions)

        widgets["id"] = Gtk.HBox(
            hexpand=False,
            vexpand=False,
            halign=Gtk.Align.END,
            valign=Gtk.Align.START,
        )
        widgets["attributes"] = CardGrid(right=True)

    def _init_ref_widgets(self):
        """
        Initialize the reference card widgets.
        """
        self.ref_eventbox = Gtk.EventBox()
        right = self.groptions.ref_mode != 1
        self.ref_widgets["id"] = Gtk.HBox(
            hexpand=False,
            vexpand=False,
            halign=Gtk.Align.END,
            valign=Gtk.Align.START,
        )
        self.ref_widgets["icons"] = CardIcons(
            self.grstate, self.groptions, right_justify=right
        )

    def _prepare_ref_layout(self):
        """
        Prepare a layout that includes a reference object section.
        """
        self._init_ref_widgets()
        self.ref_eventbox = Gtk.EventBox()
        self.ref_frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        self.ref_eventbox.add(self.ref_frame)
        if self.groptions.ref_mode in [1, 3]:
            self._prepare_horizontal_ref_layout()
        else:
            self._prepare_vertical_ref_layout()

    def _prepare_horizontal_ref_layout(self):
        """
        Prepare a horizontal reference layout, placing it on left or right.
        """
        view_obj = Gtk.HBox(hexpand=False)
        if self.groptions.ref_mode == 1:
            justify = Gtk.Align.START
            view_obj.pack_start(self.ref_eventbox, True, True, 0)
            view_obj.pack_start(self.eventbox, True, True, 0)
        else:
            justify = Gtk.Align.END
            view_obj.pack_start(self.eventbox, True, True, 0)
            view_obj.pack_start(self.ref_eventbox, True, True, 0)
        self.frame.add(view_obj)
        self.add(self.frame)

        self.ref_widgets["body"] = Gtk.VBox(
            halign=justify, valign=Gtk.Align.START
        )
        ref_body = Gtk.VBox(hexpand=False, halign=justify, margin=3)
        if "ref" in self.groptions.size_groups:
            self.groptions.size_groups["ref"].add_widget(ref_body)
        ref_body.pack_start(self.ref_widgets["id"], False, False, 0)
        ref_body.pack_start(self.ref_widgets["body"], True, True, 0)
        ref_body.pack_end(self.ref_widgets["icons"], False, False, 0)
        self.ref_frame.add(ref_body)
        self.eventbox.add(self.widgets["body"])

    def _prepare_vertical_ref_layout(self):
        """
        Prepare a vertical reference layout, placing it on top or bottom.
        """
        ref_widgets = self.ref_widgets

        self.set_spacing(3)
        if self.groptions.ref_mode == 2:
            self.pack_start(self.ref_eventbox, True, True, 0)
            self.pack_start(self.eventbox, True, True, 0)
        else:
            self.pack_start(self.eventbox, True, True, 0)
            self.pack_start(self.ref_eventbox, True, True, 0)
        ref_body = Gtk.HBox(hexpand=True, margin=3)

        ref_widgets["body"] = Gtk.HBox(halign=Gtk.Align.START)
        if "data" in self.groptions.size_groups:
            self.groptions.size_groups["data"].add_widget(ref_widgets["body"])
        ref_body.pack_start(ref_widgets["body"], True, True, 0)
        attribute_block = Gtk.VBox(hexpand=False)
        if "attributes" in self.groptions.size_groups:
            self.groptions.size_groups["attributes"].add_widget(
                attribute_block
            )
        attribute_block.pack_start(ref_widgets["id"], False, False, 0)
        attribute_block.pack_end(ref_widgets["icons"], False, False, 0)
        ref_body.pack_end(attribute_block, False, False, 0)
        self.ref_frame.add(ref_body)
        self.frame.add(self.widgets["body"])
        self.eventbox.add(self.frame)

    def _prepare_normal_layout(self):
        """
        Prepare a normal layout when no reference present.
        """
        self.frame.add(self.widgets["body"])
        if (
            self.primary
            and self.primary.obj_type == "Family"
            and not self.groptions.is_secondary
        ):
            self.add(self.frame)
        else:
            self.eventbox.add(self.frame)
            self.add(self.eventbox)

    def build_layout(self):
        """
        Construct framework for default layout.
        """
        widgets = self.widgets
        size_groups = self.groptions.size_groups

        if "age" in widgets:
            widgets["body"].pack_start(widgets["age"], False, False, 0)
            if "age" in size_groups:
                size_groups["age"].add_widget(widgets["age"])

        image_mode = self.get_option("image-mode")
        if image_mode and image_mode in [3, 4]:
            widgets["body"].pack_start(widgets["image"], False, False, 3)

        fact_block = Gtk.VBox(hexpand=True)
        if "data" in size_groups:
            size_groups["data"].add_widget(fact_block)
        widgets["body"].pack_start(fact_block, True, True, 0)
        fact_block.pack_start(widgets["title"], False, False, 0)
        fact_section = Gtk.HBox(hexpand=True, valign=Gtk.Align.START)
        fact_section.pack_start(widgets["facts"], True, True, 0)
        if "active" in self.groptions.option_space:
            fact_section.pack_start(widgets["extra"], True, True, 0)
        fact_block.pack_start(fact_section, True, True, 0)
        fact_block.pack_end(widgets["icons"], False, False, 0)

        attribute_block = Gtk.VBox(halign=Gtk.Align.END, hexpand=False)
        if "attributes" in size_groups:
            size_groups["attributes"].add_widget(attribute_block)
        widgets["body"].pack_start(attribute_block, False, False, 0)
        attribute_block.pack_start(widgets["id"], False, False, 0)
        attribute_block.pack_start(widgets["attributes"], True, True, 0)

        if image_mode in [1, 2]:
            widgets["body"].pack_end(widgets["image"], False, False, 3)
