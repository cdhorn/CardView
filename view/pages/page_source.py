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
from ..common.common_classes import GrampsOptions
from ..frames.frame_source import SourceGrampsFrame
from ..groups.group_utils import get_references_group
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class SourceProfilePage(BaseProfilePage):
    """
    Provides the source profile page view with information about the source.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
        self.active_profile = None

    @property
    def obj_type(self):
        """
        Primary object type underpinning the page.
        """
        return "Source"

    @property
    def page_type(self):
        """
        Page type.
        """
        return "Source"

    def render_page(self, header, vbox, context):
        """
        Render the page contents.
        """
        if not context:
            return

        source = context.primary_obj.obj

        groptions = GrampsOptions("options.active.source")
        self.active_profile = SourceGrampsFrame(
            self.grstate, groptions, source
        )

        groups = self.config.get("options.page.source.layout.groups").split(
            ","
        )
        obj_groups = self.get_object_groups(groups, source)

        people_list, events_list = self._get_referenced_subjects(
            groups, source
        )

        if people_list:
            groptions = GrampsOptions("options.group.people")
            args = {"title": (_("Referenced People"), _("Referenced People"))}
            obj_groups.update(
                {
                    "people": get_references_group(
                        self.grstate,
                        None,
                        args,
                        groptions=groptions,
                        obj_list=people_list,
                    )
                }
            )
        if events_list:
            groptions = GrampsOptions("options.group.event")
            args = {"title": (_("Referenced Event"), _("Referenced Events"))}
            obj_groups.update(
                {
                    "event": get_references_group(
                        self.grstate,
                        None,
                        args,
                        groptions=groptions,
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
        self.add_media_bar(vbox, source)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()

    def _get_referenced_subjects(self, groups, source):
        """
        Check backlinks as needed to get referenced subjects.
        """
        people_list = []
        events_list = []
        if "person" in groups or "event" in groups:
            for (
                obj_type,
                obj_handle,
            ) in self.grstate.dbstate.db.find_backlink_handles(
                source.get_handle()
            ):
                if obj_type != "Citation":
                    continue
                for (
                    sub_obj_type,
                    sub_obj_handle,
                ) in self.grstate.dbstate.db.find_backlink_handles(obj_handle):
                    if sub_obj_type == "Person":
                        if sub_obj_handle not in people_list:
                            people_list.append(("Person", sub_obj_handle))
                    elif sub_obj_type == "Event":
                        if sub_obj_handle not in events_list:
                            events_list.append(("Event", sub_obj_handle))
        return people_list, events_list
