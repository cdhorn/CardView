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
Source Profile Page
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
from ..frames.frame_source import SourceGrampsFrame
from ..groups.group_utils import (
    get_citations_group,
    get_media_group,
    get_notes_group,
    get_references_group,
    get_repositories_group,
    get_urls_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class SourceProfilePage(BaseProfilePage):
    """
    Provides the source profile page view with information about the source.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)

    def obj_type(self):
        return "Source"

    def page_type(self):
        return "Source"

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, source, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not source:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router, self.config, self.page_type().lower()
        )
        groptions = GrampsOptions("options.active.source")
        self.active_profile = SourceGrampsFrame(grstate, groptions, source)

        groups = self.config.get("options.page.source.layout.groups").split(",")
        obj_groups = {}

        if "repository" in groups:
            obj_groups.update(
                {"repository": get_repositories_group(grstate, source)}
            )
        if "citation" in groups:
            obj_groups.update(
                {"citation": get_citations_group(grstate, source)}
            )
        if "url" in groups:
            obj_groups.update({"url": get_urls_group(grstate, source)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, source)})
        if "media" in groups:
            obj_groups.update({"media": get_media_group(grstate, source)})

        people_list = []
        events_list = []
        if "person" in groups or "event" in groups:
            for obj_type, obj_handle in self.dbstate.db.find_backlink_handles(
                source.get_handle()
            ):
                if obj_type == "Citation":
                    for (
                        sub_obj_type,
                        sub_obj_handle,
                    ) in self.dbstate.db.find_backlink_handles(obj_handle):
                        if sub_obj_type == "Person":
                            if sub_obj_handle not in people_list:
                                people_list.append(("Person", sub_obj_handle))
                        elif sub_obj_type == "Event":
                            if sub_obj_handle not in events_list:
                                events_list.append(("Event", sub_obj_handle))

        if people_list:
            groptions = GrampsOptions("options.group.people")
            obj_groups.update(
                {
                    "people": get_references_group(
                        grstate,
                        None,
                        groptions=groptions,
                        title_plural=_("Referenced People"),
                        title_single=_("Referenced People"),
                        obj_list=people_list,
                    )
                }
            )
        if events_list:
            groptions = GrampsOptions("options.group.event")
            obj_groups.update(
                {
                    "event": get_references_group(
                        grstate,
                        None,
                        groptions=groptions,
                        title_plural=_("Referenced Events"),
                        title_single=_("Referenced Events"),
                        obj_list=events_list,
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
