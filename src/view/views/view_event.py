#
# Gramps - a GTK+/GNOME based genealogy program
#
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
EventObjectView
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
from ..groups.group_builder import get_references_group
from .view_base import GrampsObjectView
from .view_const import FRAME_MAP

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# EventObjectView Class
#
# -------------------------------------------------------------------------
class EventObjectView(GrampsObjectView):
    """
    Provides the event object view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        event = self.grcontext.primary_obj.obj

        groptions = GrampsOptions("active.event")
        self.view_object = FRAME_MAP["Event"](
            self.grstate,
            groptions,
            event,
        )
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        groups = self.grstate.config.get("layout.event.groups").split(",")
        object_groups = self.get_object_groups(
            "layout.event", groups, event, age_base=event.get_date_object()
        )
        if "people" in groups or "family" in groups:
            self.add_participant_groups(event, object_groups)

        self.view_body = self.render_group_view(object_groups)

    def add_participant_groups(self, event, object_groups):
        """
        Evaluate and add the participant groups as needed.
        """
        people_list = []
        family_list = []

        for (
            obj_type,
            obj_handle,
        ) in self.grstate.dbstate.db.find_backlink_handles(event.handle):
            if obj_type == "Person" and obj_handle not in people_list:
                people_list.append(("Person", obj_handle))
            elif obj_type == "Family" and obj_handle not in family_list:
                family_list.append(("Family", obj_handle))

        if people_list:
            groptions = GrampsOptions("group.people")
            args = {
                "title": (
                    _("Individual Participants"),
                    _("Individual Participants"),
                )
            }
            if event.get_date_object():
                args["age_base"] = event.get_date_object()
            object_groups.update(
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

        if family_list:
            groptions = GrampsOptions("group.family")
            args = {
                "title": (_("Family Participants"), _("Family Participants")),
            }
            if event.get_date_object():
                args["age_base"] = event.get_date_object()
            object_groups.update(
                {
                    "family": get_references_group(
                        self.grstate,
                        None,
                        args,
                        groptions=groptions,
                        obj_list=family_list,
                    )
                }
            )
