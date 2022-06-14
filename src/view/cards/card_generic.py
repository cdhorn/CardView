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
GenericCard
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
import pickle
import re

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Span
from gramps.gen.utils.db import navigation_label
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import WarningDialog
from gramps.gui.utils import match_primary_mask

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_classes import GrampsContext, GrampsObject
from ..common.common_const import (
    BUTTON_MIDDLE,
    BUTTON_PRIMARY,
    BUTTON_SECONDARY,
)
from ..common.common_utils import button_pressed, button_released
from ..menus.menu_bookmarks import build_bookmarks_menu
from ..menus.menu_config import build_config_menu
from ..menus.menu_templates import build_templates_menu
from .card_view import CardView

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GenericCard Class
#
# ------------------------------------------------------------------------
class GenericCard(CardView):
    """
    Provides core methods for working with a generic card.
    """

    def __init__(self, grstate, groptions, *_dummy_args, **kwargs):
        CardView.__init__(self, grstate, groptions)
        self.primary = None
        self.secondary = None
        self.reference_base = None
        self.reference = None
        self.focus = None
        self.dnd_drop_targets = []
        self.css = ""
        self.init_layout()
        self.eventbox.connect("button-press-event", self.cb_button_pressed)
        self.eventbox.connect("button-release-event", self.cb_button_released)

    def cb_button_pressed(self, obj, event):
        """
        Handle button pressed.
        """
        if button_pressed(event, BUTTON_SECONDARY):
            if match_primary_mask(event.state):
                build_bookmarks_menu(self, self.grstate, event)
                return True
            self.build_context_menu(obj, event)
            return True
        return False

    def cb_button_released(self, obj, event):
        """
        Handle button released.
        """
        if button_released(event, BUTTON_PRIMARY):
            if match_primary_mask(event.state):
                build_templates_menu(self, self.grstate, event)
                return True
        return False

    def switch_object(self, _dummy_obj, _dummy_event, obj_type, obj_or_handle):
        """
        Change active object for the view.
        """
        if isinstance(obj_or_handle, str):
            obj = self.grstate.fetch(obj_type, obj_or_handle)
        else:
            obj = obj_or_handle
        context = GrampsContext(obj, None, None)
        return self.grstate.load_page(context.pickled)

    def build_context_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click, should be defined in
        derived classes.
        """
        return True

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("display.border-width")
        color = self.get_color_css()
        self.css = "".join(
            (
                ".frame { border: solid; border-radius: 5px; border-width: ",
                str(border),
                "px; ",
                color,
                " }",
            )
        ).encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(self.css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
        if self.groptions.ref_mode in [2, 4]:
            context = self.ref_frame.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            context.add_class("frame")

    def get_color_css(self):
        """
        For derived objects to set their color scheme if in use.
        """
        scheme = global_config.get("colors.scheme")
        background = self.grstate.config.get(
            "display.default-background-color"
        )
        return "background-color: %s;" % background[scheme]

    def get_css_style(self):
        """
        Return css style string.
        """
        return self.css
