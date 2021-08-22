# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
ChildRef Profile Page
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk


# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.widgets.reorderfam import Reorder


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames.frame_classes import GrampsState, GrampsOptions
from ..frames.frame_const import _LEFT_BUTTON
from ..frames.frame_child import ChildGrampsFrame
from ..frames.frame_couple import CoupleGrampsFrame
from ..frames.frame_utils import button_activated
from ..groups.group_utils import (
    get_citations_group,
    get_notes_group,
    get_urls_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class ChildRefProfilePage(BaseProfilePage):
    """
    Provides the child profile page view with information about the
    status of a child in a family.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)
        self.order_action = None
        self.family_action = None
        self.reorder_sensitive = None
        self.child = None
        self.colors = None
        self.active_profile = None

    def obj_type(self):
        """
        Primary object page focused on.
        """
        return "Person"

    def page_type(self):
        """
        Page type.
        """
        return "ChildRef"

    def define_actions(self, view):
        """
        Define page actions.
        """
        pass

    def enable_actions(self, uimanager, person):
        """
        Enable page actions.
        """
        pass

    def disable_actions(self, uimanager):
        """
        Disable page actions.
        """
        pass

    def render_page(self, header, vbox, person, secondary=None):
        """
        Render view for the page.
        """
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not person or not secondary:
            return

        family = self.dbstate.db.get_family_from_handle(secondary)
        for child_ref in family.get_child_ref_list():
            if child_ref.ref == person.get_handle():
                break

        grstate = GrampsState(
            self.dbstate,
            self.uistate,
            self.callback_router,
            self.config,
            self.page_type().lower(),
        )
        groptions = GrampsOptions("options.active.family")
        groptions.set_vertical(False)
        family_frame = CoupleGrampsFrame(
            grstate,
            groptions,
            family,
        )
        groptions = GrampsOptions("options.active.person")
        groptions.set_backlink(family.get_handle())
        groptions.set_ref_mode(3)
        self.active_profile = ChildGrampsFrame(
            grstate,
            groptions,
            person,
            child_ref,
        )
        vheader = Gtk.VBox(spacing=3)
        vheader.pack_start(family_frame, False, False, 0)
        vheader.pack_start(self.active_profile, False, False, 0)

        groups = self.config.get("options.page.childref.layout.groups").split(
            ","
        )
        obj_groups = {}

        if "citation" in groups:
            obj_groups.update(
                {"citation": get_citations_group(grstate, child_ref)}
            )
        if "url" in groups:
            obj_groups.update({"url": get_urls_group(grstate, child_ref)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, child_ref)})
        body = self.render_group_view(obj_groups)

        if self.config.get("options.global.pin-header"):
            header.pack_start(vheader, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(vheader, False, False, 0)
        self.child = body
        vbox.pack_start(self.child, True, True, 0)
        vbox.show_all()

    def reorder_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *obj):
        if self.active_profile:
            try:
                Reorder(
                    self.dbstate,
                    self.uistate,
                    [],
                    self.active_profile.obj.get_handle(),
                )
            except WindowActiveError:
                pass

    def add_spouse(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_spouse()

    def select_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_existing_parents()

    def add_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_parents()
