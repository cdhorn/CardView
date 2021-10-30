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
GrampsFrameView class for managing the frame widgets and layout.
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
from ..common.common_classes import GrampsConfig
from .frame_widgets import (
    GrampsFrameGrid,
    GrampsFrameId,
    GrampsFrameIndicators,
    GrampsFrameTags,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsFrameView class
#
# ------------------------------------------------------------------------
class GrampsFrameView(Gtk.VBox, GrampsConfig):
    """
    A simple class to encapsulate the widget layout for a Gramps frame.
    """

    def __init__(self, grstate, groptions, cbrouter):
        Gtk.VBox.__init__(self, hexpand=True, vexpand=False)
        GrampsConfig.__init__(self, grstate, groptions)
        self.cbrouter = cbrouter
        self.frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        self.widgets = {"body": Gtk.HBox(hexpand=True, margin=3)}
        self.eventbox = Gtk.EventBox()

        self.ref_frame = None
        self.ref_widgets = {}
        self.ref_eventbox = None

    def init_layout(self, secondary=None):
        """
        Initialize the default frame layout.
        """
        self._init_widgets()
        if secondary and secondary.is_reference:
            self._prepare_ref_layout()
        else:
            self._prepare_normal_layout()

    def _init_widgets(self):
        """
        Initialize primary frame widgets.
        """
        self.widgets["image"] = Gtk.Box()
        if self.get_option("show-age") or self.groptions.age_base:
            self.widgets["age"] = Gtk.VBox(
                margin_right=3,
                margin_left=3,
                margin_top=3,
                margin_bottom=3,
                spacing=2,
            )
        self.widgets["title"] = Gtk.HBox(
            hexpand=True,
            vexpand=False,
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
        )
        self.widgets["facts"] = GrampsFrameGrid(
            self.grstate, self.groptions, self.cbrouter
        )
        self.widgets["extra"] = GrampsFrameGrid(
            self.grstate, self.groptions, self.cbrouter
        )
        if self.get_option("tag-format"):
            self.widgets["tags"] = GrampsFrameTags(
                self.grstate, self.groptions
            )

        self.widgets["id"] = GrampsFrameId(self.grstate, self.groptions)
        self.widgets["attributes"] = GrampsFrameGrid(
            self.grstate, self.groptions, self.cbrouter, right=True
        )
        if self.get_option("options.global.enable-child-indicators"):
            self.widgets["indicators"] = GrampsFrameIndicators(
                self.grstate, self.groptions
            )

    def _init_ref_widgets(self):
        """
        Initialize the reference frame widgets.
        """
        self.ref_eventbox = Gtk.EventBox()
        self.ref_widgets["id"] = GrampsFrameId(self.grstate, self.groptions)
        if "indicators" in self.widgets:
            self.ref_widgets["indicators"] = GrampsFrameIndicators(
                self.grstate, self.groptions
            )

    def _prepare_ref_layout(self):
        """
        Prepare a layout that includes a reference object section.
        """
        self._init_ref_widgets()
        self.ref_eventbox = Gtk.EventBox()
        self.ref_frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        self.ref_eventbox.add(self.ref_frame)
        if self.groptions.ref_mode == 1:
            self._prepare_horizontal_ref_layout()
        else:
            self._prepare_vertical_ref_layout()

    def _prepare_horizontal_ref_layout(self):
        """
        Prepare a horizontal reference layout, placing it on right side.
        """
        view_obj = Gtk.HBox(hexpand=True)
        view_obj.pack_start(self.eventbox, True, True, 0)
        view_obj.pack_start(self.ref_eventbox, True, True, 0)
        self.frame.add(view_obj)
        self.add(self.frame)

        self.ref_widgets["body"] = Gtk.VBox(
            halign=Gtk.Align.END, valign=Gtk.Align.START
        )
        ref_body = Gtk.VBox(hexpand=True, halign=Gtk.Align.END, margin=3)
        if "ref" in self.groptions.size_groups:
            self.groptions.size_groups["ref"].add_widget(ref_body)
        ref_body.pack_start(
            self.ref_widgets["id"], expand=False, fill=False, padding=0
        )
        ref_body.pack_start(
            self.ref_widgets["body"], expand=True, fill=True, padding=0
        )
        ref_body.pack_end(
            self.ref_widgets["indicators"], expand=False, fill=False, padding=0
        )
        self.ref_frame.add(ref_body)
        self.eventbox.add(self.widgets["body"])

    def _prepare_vertical_ref_layout(self):
        """
        Prepare a vertical reference layout, placing it on top or bottom.
        """
        self.set_spacing(3)
        if self.groptions.ref_mode == 0:
            self.pack_start(self.ref_eventbox, True, True, 0)
            self.pack_start(self.eventbox, True, True, 0)
        elif self.groptions.ref_mode == 2:
            self.pack_start(self.eventbox, True, True, 0)
            self.pack_start(self.ref_eventbox, True, True, 0)
        ref_body = Gtk.HBox(hexpand=True, margin=3)

        self.ref_widgets["body"] = Gtk.HBox(halign=Gtk.Align.START)
        ref_body.pack_start(
            self.ref_widgets["body"], expand=True, fill=True, padding=0
        )
        attribute_block = Gtk.VBox(hexpand=False)
        attribute_block.pack_start(
            self.ref_widgets["id"], expand=False, fill=False, padding=0
        )
        attribute_block.pack_end(
            self.ref_widgets["indicators"], expand=False, fill=False, padding=0
        )
        ref_body.pack_end(attribute_block, expand=False, fill=False, padding=0)
        self.ref_frame.add(ref_body)
        self.frame.add(self.widgets["body"])
        self.eventbox.add(self.frame)

    def _prepare_normal_layout(self):
        """
        Prepare a normal layout when no reference present.
        """
        self.frame.add(self.widgets["body"])
        if self.primary.obj_type == "Family" and not self.secondary:
            self.add(self.frame)
        else:
            self.eventbox.add(self.frame)
            self.add(self.eventbox)

    def build_layout(self):
        """
        Construct framework for default layout.
        """
        image_mode = self.get_option("image-mode")
        if image_mode and image_mode in [3, 4]:
            self.widgets["body"].pack_start(
                self.widgets["image"], expand=False, fill=False, padding=0
            )

        if "age" in self.widgets:
            self.widgets["body"].pack_start(
                self.widgets["age"], expand=False, fill=False, padding=0
            )
            if "age" in self.groptions.size_groups:
                self.groptions.size_groups["age"].add_widget(
                    self.widgets["age"]
                )

        fact_block = Gtk.VBox(hexpand=True)
        if "data" in self.groptions.size_groups:
            self.groptions.size_groups["data"].add_widget(fact_block)
        self.widgets["body"].pack_start(
            fact_block, expand=True, fill=True, padding=0
        )
        fact_block.pack_start(
            self.widgets["title"], expand=False, fill=False, padding=0
        )
        fact_section = Gtk.HBox(hexpand=True, valign=Gtk.Align.START)
        fact_section.pack_start(
            self.widgets["facts"], expand=True, fill=True, padding=0
        )
        fact_section.pack_start(
            self.widgets["extra"], expand=True, fill=True, padding=0
        )
        fact_block.pack_start(fact_section, expand=True, fill=True, padding=0)
        if "tags" in self.widgets:
            fact_block.pack_end(
                self.widgets["tags"], expand=False, fill=False, padding=0
            )

        attribute_block = Gtk.VBox(halign=Gtk.Align.END, hexpand=False)
        if "attributes" in self.groptions.size_groups:
            self.groptions.size_groups["attributes"].add_widget(
                attribute_block
            )
        self.widgets["body"].pack_end(
            attribute_block, expand=False, fill=False, padding=0
        )
        attribute_block.pack_start(
            self.widgets["id"], expand=False, fill=False, padding=0
        )
        attribute_block.pack_start(
            self.widgets["attributes"], expand=True, fill=True, padding=0
        )
        if "indicators" in self.widgets:
            attribute_block.pack_end(
                self.widgets["indicators"], expand=False, fill=False, padding=0
            )

        if image_mode in [1, 2]:
            self.widgets["body"].pack_start(
                self.widgets["image"], expand=False, fill=False, padding=0
            )
