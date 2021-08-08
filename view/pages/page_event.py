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
Event Profile Page
"""

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
from ..frames.frame_classes import GrampsState, GrampsOptions
from ..frames.frame_event import EventGrampsFrame
from ..groups.group_utils import (
    get_citations_group,
    get_media_group,
    get_notes_group,
    get_references_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class EventProfilePage(BaseProfilePage):
    """
    Provides the event profile page view with information about the event.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)

    def obj_type(self):
        return "Event"

    def page_type(self):
        return "Event"

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, event, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not event:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router, self.config, self.page_type().lower()
        )
        groptions = GrampsOptions("options.active.event")
        self.active_profile = EventGrampsFrame(
            grstate,
            groptions,
            None,
            event,
            None,
            None,
            None,
            None,
        )

        groups = self.config.get("options.page.event.layout.groups").split(",")
        obj_groups = {}

        if "citation" in groups:
            obj_groups.update({"citation": get_citations_group(grstate, event)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, event)})
        if "media" in groups:
            obj_groups.update({"media": get_media_group(grstate, event)})

        people_list = []
        family_list = []
        if "people" in groups or "family" in groups:
            for obj_type, obj_handle in self.dbstate.db.find_backlink_handles(
                event.get_handle()
            ):
                if obj_type == "Person" and obj_handle not in people_list:
                    people_list.append(("Person", obj_handle))
                elif obj_type == "Family" and obj_handle not in family_list:
                    family_list.append(("Family", obj_handle))

        if people_list:
            groptions = GrampsOptions("options.group.people")
            obj_groups.update(
                {
                    "people": get_references_group(
                        grstate,
                        None,
                        groptions=groptions,
                        title_plural=_("Individual Participants"),
                        title_single=_("Individial Participants"),
                        obj_list=people_list,
                    )
                }
            )
        if family_list:
            groptions = GrampsOptions("options.group.family")
            obj_groups.update(
                {
                    "family": get_references_group(
                        grstate,
                        None,
                        groptions=groptions,
                        title_plural=_("Family Participants"),
                        title_single=_("Family Participants"),
                        obj_list=family_list,
                    )
                }
            )

        body = self.render_group_view(obj_groups)
        if self.config.get("options.global.pin-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
