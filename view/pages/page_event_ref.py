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
EventRef Profile Page
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..common.common_utils import get_gramps_object_type
from ..frames.frame_couple import CoupleGrampsFrame
from ..frames.frame_event import EventGrampsFrame
from ..frames.frame_person import PersonGrampsFrame
from ..groups.group_utils import get_references_group
from .page_base import BaseProfilePage
from .page_const import FRAME_MAP

_ = glocale.translation.sgettext


class EventRefProfilePage(BaseProfilePage):
    """
    Provides the event reference profile page view with information about the
    event reference.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
        self.active_profile = None

    @property
    def obj_type(self):
        return "Event"

    @property
    def page_type(self):
        return "EventRef"

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, primary, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not primary or not secondary:
            return

        primary_type = get_gramps_object_type(primary)
        (option, frame) = FRAME_MAP[primary_type]
        groptions = GrampsOptions(option)
        primary_frame = frame(self.grstate, groptions, primary)

        if primary_type == "Person":
            event_person = primary
            event_family = None
        else:
            event_person = None
            event_family = primary

        event_ref = None
        for event_ref in primary.get_event_ref_list():
            if event_ref.ref == secondary:
                break
        event = self.grstate.fetch("Event", event_ref.ref)

        groptions = GrampsOptions("options.active.event")
        groptions.set_ref_mode(2)
        self.active_profile = EventGrampsFrame(
            self.grstate,
            groptions,
            event_person,
            event,
            event_ref,
            event_person,
            event_family,
            "self",
        )
        vheader = Gtk.VBox(spacing=3)
        vheader.pack_start(primary_frame, False, False, 0)
        vheader.pack_start(self.active_profile, False, False, 0)

        groups = self.config.get("options.page.eventref.layout.groups").split(
            ","
        )
        obj_groups = self.get_object_groups(groups, event_ref)
        body = self.render_group_view(obj_groups)

        if self.config.get("options.global.pin-header"):
            header.pack_start(vheader, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(vheader, False, False, 0)
        self.child = body
        vbox.pack_start(body, True, True, 0)
        vbox.show_all()
        return
