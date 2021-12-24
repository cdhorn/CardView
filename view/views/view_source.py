# Gramps - a GTK+/GNOME based genealogy program
#
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
SourceObjectView
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


class SourceObjectView(GrampsObjectView):
    """
    Provides the source object view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        source = self.grcontext.primary_obj.obj

        groptions = GrampsOptions("options.active.source")
        self.view_object = FRAME_MAP["Source"](self.grstate, groptions, source)
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        group_list = self.grstate.config.get(
            "options.page.source.layout.groups"
        ).split(",")
        object_groups = self.get_object_groups(group_list, source)
        if (
            "people" in group_list
            or "event" in group_list
            or "place" in group_list
        ):
            self.add_cited_subject_groups(source, object_groups)

        self.view_body = self.render_group_view(object_groups)

    def add_cited_subject_groups(self, source, object_groups):
        """
        Evaluate and add the groups for cited subjects found in the source.
        """
        people_list = []
        events_list = []
        places_list = []

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
                elif (
                    sub_obj_type == "Place"
                    and sub_obj_handle not in places_list
                ):
                    places_list.append(("Place", sub_obj_handle))

        if "people" in object_groups and people_list:
            groptions = GrampsOptions("options.group.people")
            args = {"title": (_("Cited People"), _("Cited People"))}
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

        if "event" in object_groups and events_list:
            groptions = GrampsOptions("options.group.event")
            args = {"title": (_("Cited Event"), _("Cited Events"))}
            object_groups.update(
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

        if "place" in object_groups and places_list:
            groptions = GrampsOptions("options.group.place")
            args = {"title": (_("Cited Place"), _("Cited Places"))}
            object_groups.update(
                {
                    "place": get_references_group(
                        self.grstate,
                        None,
                        args,
                        groptions=groptions,
                        obj_list=places_list,
                    )
                }
            )
