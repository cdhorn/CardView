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
Attribute Profile Page
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.uimanager import ActionGroup
from gramps.gui.widgets.reorderfam import Reorder


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames.frame_attribute import AttributeGrampsFrame
from ..frames.frame_citation import CitationGrampsFrame
from ..frames.frame_classes import GrampsState, GrampsOptions
from ..frames.frame_const import _LEFT_BUTTON
from ..frames.frame_couple import CoupleGrampsFrame
from ..frames.frame_event import EventGrampsFrame
from ..frames.frame_image import ImageGrampsFrame
from ..frames.frame_person import PersonGrampsFrame
from ..frames.frame_source import SourceGrampsFrame
from ..frames.frame_utils import button_activated, get_gramps_object_type
from ..groups.group_utils import (
    get_citations_group,
    get_notes_group,
    get_urls_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class AttributeProfilePage(BaseProfilePage):
    """
    Provides the attribute profile page view with information about the
    attribute for an object.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)
        self.child = None
        self.colors = None
        self.active_profile = None
        self.focus_type = "Person"

    def obj_type(self):
        return self.focus_type

    def page_type(self):
        return "Attribute"

    def define_actions(self, view):
        pass

    def enable_actions(self, uimanager, person):
        pass

    def disable_actions(self, uimanager):
        pass

    def render_page(self, header, vbox, primary, secondary):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not primary:
            return
        
        self.focus_type = get_gramps_object_type(primary)

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router, self.config, self.page_type().lower()
        )
        if self.focus_type == "Person":
            groptions = GrampsOptions("options.active.person")
            self.active_profile = PersonGrampsFrame(grstate, groptions, primary)
        elif self.focus_type == "Family":
            groptions = GrampsOptions("options.active.family")
            self.active_profile = CoupleGrampsFrame(grstate, groptions, primary)
        elif self.focus_type == "Event":
            groptions = GrampsOptions("options.active.event")
            self.active_profile = EventGrampsFrame(grstate, groptions, primary)
        elif self.focus_type == "Media":
            groptions = GrampsOptions("options.active.media")
            self.active_profile = ImageGrampsFrame(grstate, groptions, primary)
        elif self.focus_type == "Source":
            groptions = GrampsOptions("options.active.source")
            self.active_profile = SourceGrampsFrame(grstate, groptions, primary)
        elif self.focus_type == "Citation":
            groptions = GrampsOptions("options.active.citation")
            self.active_profile = CitationGrampsFrame(grstate, groptions, primary)

        groptions = GrampsOptions("options.active.attribute")
        frame = AttributeGrampsFrame(grstate, groptions, primary, secondary)

        groups = self.config.get("options.page.attribute.layout.groups").split(",")
        obj_groups = {}

        if "citation" in groups:
            obj_groups.update({"citation": get_citations_group(grstate, secondary)})
        if "url" in groups:
            obj_groups.update({"url": get_urls_group(grstate, secondary)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, secondary)})
        body = self.render_group_view(obj_groups)

        if self.config.get("options.global.pin-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.pack_start(frame, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
            vbox.pack_start(frame, False, False, 0)
        self.child = body
        vbox.pack_start(self.child, True, True, 0)
        vbox.show_all()
        return True
