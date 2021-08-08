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
TagGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import pickle
import re


# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk, Gdk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.views.tags import OrganizeTagsDialog, EditTag
from gramps.gen.errors import WindowActiveError
from gramps.gui.ddtargets import DdTargets


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_base import GrampsFrame
from .frame_classes import GrampsConfig, GrampsObject
from .frame_const import _EDITORS, _LEFT_BUTTON, _RIGHT_BUTTON
from .frame_utils import (
    button_activated,
    menu_item,
    submenu_item,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TagGrampsFrame class
#
# ------------------------------------------------------------------------
class TagGrampsFrame(GrampsFrame):
    """
    The TagGrampsFrame class exposes information about a tag.
    """

    def __init__(self, grstate, groptions, tag):
        GrampsFrame.__init__(self, grstate, groptions, tag)
        self.action_menu = None

        vcontent = Gtk.VBox()
        self.title = Gtk.HBox(spacing=6)
        vcontent.pack_start(self.title, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        body = Gtk.HBox(hexpand=True, margin=3)
        body.pack_start(vcontent, expand=True, fill=True, padding=0)
        self.frame.add(body)
        self.eventbox.add(self.frame)
        self.add(self.eventbox)

        image = Gtk.Image()
        image.set_from_icon_name("gramps-tag", Gtk.IconSize.BUTTON)
        self.title.pack_start(image, False, False, 0)
        label = Gtk.Label(use_markup=True, label="<b>{}</b>".format(tag.name))
        self.title.pack_start(label, False, False, 0)
        
        self.facts_grid.attach(self.make_label("{}:".format(_("Priority"))), 0, 0, 1, 1)
        self.facts_grid.attach(self.make_label(str(tag.priority)), 1, 0, 1, 1)
        label = Gtk.Label(label="{}:".format(_("Color")))
        self.facts_grid.attach(self.make_label("{}:".format(_("Color"))), 0, 1, 1, 1)
        
        label = self.make_label(tag.color)
        css = ".label {{ margin: 0px; padding: 0px; font-size: x-small; color: black; background-color: {}; }}".format(
            tag.color[:7]
        )
        css_class = "label"
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = label.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class(css_class)
        self.facts_grid.attach(label, 1, 1, 1, 1)
        self.set_css_style()

    def build_action_menu(self, obj, event):
        """
        Build the action menu for the tag.
        """
        menu = Gtk.Menu()
        menu.add(menu_item("gramps-tag", _("Edit tag"), self.edit_tag))
        menu.add(
            menu_item("gramps-tag", _("Organize tags"), self.organize_tags)
        )
        menu.show_all()
        if Gtk.get_minor_version() >= 22:
            menu.popup_at_pointer(event)
        else:
            menu.popup(
                None, None, None, None, event.button, event.time
            )

    def edit_tag(self, _dummy_obj):
        """
        Create a new tag.
        """
        try:
            EditTag(self.grstate.dbstate.db, self.grstate.uistate, [], self.primary.obj)
        except WindowActiveError:
            pass

    def organize_tags(self, _dummy_obj):
        """
        Organize tags.
        """
        try:
            OrganizeTagsDialog(
                self.grstate.dbstate.db, self.grstate.uistate, []
            )
        except WindowActiveError:
            pass

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("options.global.border-width")
        color = self.get_color_css()
        css = ".frame {{ border-width: {}px; {} }}".format(border, color)
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")

    def get_color_css(self):
        """
        For derived objects to set their color scheme if in use.
        """
        return ""
