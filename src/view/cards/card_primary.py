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
PrimaryCard
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
import time

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
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_classes import GrampsContext
from ..fields.field_builder import field_builder
from ..menus.menu_utils import (
    add_attributes_menu,
    add_bookmark_menu_option,
    add_citations_menu,
    add_clipboard_menu_option,
    add_delete_menu_option,
    add_double_separator,
    add_edit_menu_option,
    add_media_menu,
    add_notes_menu,
    add_privacy_menu_option,
    add_tags_menu,
    add_urls_menu,
    show_menu,
)
from .card_object import ObjectCard
from .card_widgets import GrampsImage
from .card_utils import load_metadata

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PrimaryCard Class
#
# ------------------------------------------------------------------------
class PrimaryCard(ObjectCard):
    """
    The PrimaryCard class provides core methods for constructing the
    view and working with the primary Gramps object it exposes.
    """

    def __init__(self, grstate, groptions, primary_obj, reference_tuple=None):
        ObjectCard.__init__(
            self,
            grstate,
            groptions,
            primary_obj,
            reference_tuple=reference_tuple,
        )
        if not groptions.bar_mode:
            self.build_layout()
            self.load_layout()

    def load_layout(self):
        """
        Load standard portions of layout.
        """
        option_space = self.groptions.option_space
        if "spouse" in option_space or "parent" in option_space:
            if "active" in option_space:
                image_mode = self.get_option("active.family.image-mode")
            else:
                image_mode = self.get_option("group.family.image-mode")
        else:
            image_mode = self.get_option("image-mode")
        if image_mode and "media" not in option_space:
            self.load_image(image_mode)
        load_metadata(
            self.widgets["id"], self.grstate, self.groptions, self.primary
        )
        self.load_attributes()
        self.widgets["icons"].load(self.primary, title=self.get_title())

    def load_image(self, image_mode, media_ref=None, crop=True):
        """
        Load primary image for the object if found.
        """
        size = int(image_mode in [2, 4])
        active = "active" in self.groptions.option_space
        image = GrampsImage(
            self.grstate, self.primary.obj, media_ref=media_ref, active=active
        )
        image.load(size, crop)
        self.widgets["image"].add(image)
        if "image" in self.groptions.size_groups:
            self.groptions.size_groups["image"].add_widget(image)

    def load_grid(self, grid_key, option_prefix, args=None):
        """
        Load any user defined attributes.
        """
        assert grid_key in self.widgets
        grid = self.widgets[grid_key]
        args = args or {}
        args.update(
            {
                "get_label": self.get_label,
                "get_link": self.get_link,
            }
        )
        for count in range(1, 11):
            option = self.get_option(
                "%s%s" % (option_prefix, str(count)), full=False
            )
            if (
                option
                and option[0] != "None"
                and len(option) > 1
                and option[1]
            ):
                labels = field_builder(
                    self.grstate, self.primary.obj, option[0], option[1], args
                )
                for (label, value) in labels:
                    grid.add_fact(value, label=label)

    def load_attributes(self):
        """
        Load any user defined attributes.
        """
        args = {
            "skip_labels": not self.get_option("rfield-show-labels"),
        }
        self.load_grid("attributes", "rfield-", args)

    def add_fact(self, fact, label=None, extra=False):
        """
        Add a fact.
        """
        if extra and "extra" in self.widgets:
            self.widgets["extra"].add_fact(fact, label=label)
        else:
            self.widgets["facts"].add_fact(fact, label=label)

    def _primary_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing largely common to all primary objects.
        """
        if DdTargets.MEDIAOBJ.drag_type == dnd_type:
            action = action_handler("Media", self.grstate, self.primary)
            action.add_new_media_ref(obj_or_handle)
            return True
        if DdTargets.ATTRIBUTE.drag_type == dnd_type:
            action = action_handler("Attribute", self.grstate, self.primary)
            action.added_attribute(obj_or_handle)
            return True
        if DdTargets.URL.drag_type == dnd_type:
            action = action_handler("Url", self.grstate, self.primary)
            action.added_url(obj_or_handle)
            return True
        return self._base_drop_handler(dnd_type, obj_or_handle, data)

    def build_context_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click. First action will always be
        edit, then any custom actions of the derived children, then the global
        actions supported for all objects enabled for them.
        """
        context_menu = Gtk.Menu()
        add_edit_menu_option(self.grstate, context_menu, self.primary)
        if self.grstate.config.get(
            "menu.delete"
        ) and not self.grstate.config.get("menu.delete-bottom"):
            add_delete_menu_option(self.grstate, context_menu, self.primary)
        self.add_custom_actions(context_menu)
        add_attributes_menu(self.grstate, context_menu, self.primary)
        add_citations_menu(self.grstate, context_menu, self.primary)
        add_media_menu(self.grstate, context_menu, self.primary)
        add_notes_menu(self.grstate, context_menu, self.primary)
        add_tags_menu(
            self.grstate,
            context_menu,
            self.primary,
            sort_by_name=self.grstate.config.get(
                "indicator.tags-sort-by-name"
            ),
        )
        add_urls_menu(self.grstate, context_menu, self.primary)
        add_clipboard_menu_option(
            self.grstate, context_menu, self.copy_to_clipboard
        )
        add_bookmark_menu_option(self.grstate, context_menu, self.primary)
        add_privacy_menu_option(self.grstate, context_menu, self.primary)
        add_double_separator(context_menu)
        if self.primary.obj.change:
            text = "%s %s" % (
                _("Last changed"),
                time.strftime(
                    "%x %X", time.localtime(self.primary.obj.change)
                ),
            )
        else:
            text = _("Never changed")
        label = Gtk.MenuItem(label=text)
        label.set_sensitive(False)
        context_menu.append(label)
        if self.grstate.config.get("menu.delete") and self.grstate.config.get(
            "menu.delete-bottom"
        ):
            add_double_separator(context_menu)
            add_delete_menu_option(self.grstate, context_menu, self.primary)
        return show_menu(context_menu, self, event)

    def add_custom_actions(self, context_menu):
        """
        For derived objects to inject their own actions into the menu.
        """

    def goto_person(self, _dummy_obj, handle):
        """
        Change active person for the view.
        """
        person = self.grstate.fetch("Person", handle)
        context = GrampsContext(person, None, None)
        self.grstate.load_page(context.pickled)

    def copy_to_clipboard(self, _dummy_obj):
        """
        Copy current object to the clipboard.
        """
        self.grstate.copy_to_clipboard(
            self.primary.obj_type, self.primary.obj.handle
        )
