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
from .view_const import CARD_MAP

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# SourceObjectView Class
#
# -------------------------------------------------------------------------
class SourceObjectView(GrampsObjectView):
    """
    Provides the source object view.
    """

    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        source = self.grcontext.primary_obj.obj

        groptions = GrampsOptions("active.source")
        self.view_object = CARD_MAP["Source"](self.grstate, groptions, source)
        self.view_focus = self.wrap_focal_widget(self.view_object)
        self.view_header.pack_start(self.view_focus, False, False, 0)

        groups = self.grstate.config.get("layout.source.groups").split(",")
        object_groups = self.get_object_groups("layout.source", groups, source)
        if "people" in groups or "event" in groups or "place" in groups:
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
        ) in self.grstate.dbstate.db.find_backlink_handles(source.handle):
            if obj_type == "Citation":
                self.__extract_references(
                    obj_handle, people_list, events_list, places_list
                )

        if "people" in object_groups and people_list:
            groptions = GrampsOptions("group.people")
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
            groptions = GrampsOptions("group.event")
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
            groptions = GrampsOptions("group.place")
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

    def __extract_references(
        self, handle, people_list, events_list, places_list
    ):
        """
        Extract person, event and place references for an object.
        """
        for (
            obj_type,
            obj_handle,
        ) in self.grstate.dbstate.db.find_backlink_handles(handle):
            if obj_type == "Person":
                if obj_handle not in people_list:
                    people_list.append(("Person", obj_handle))
            elif obj_type == "Event":
                if obj_handle not in events_list:
                    events_list.append(("Event", obj_handle))
            elif obj_type == "Place" and obj_handle not in places_list:
                places_list.append(("Place", obj_handle))
