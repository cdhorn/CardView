#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
TimelineGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_event import EventGrampsFrame
from ..frames.frame_utils import get_gramps_object_type
from .group_list import GrampsFrameGroupList
from ..timeline import EVENT_CATEGORIES, RELATIVES, Timeline

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TimelineGrampsFrameGroup
#
# ------------------------------------------------------------------------
class TimelineGrampsFrameGroup(GrampsFrameGroupList):
    """
    The TimelineGrampsFrameGroup generates an event timeline for a person
    that may also optionally include events for close family if choosen.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(self, grstate, groptions, enable_drop=False)
        self.obj = obj
        self.obj_type, skip1, skip2 = get_gramps_object_type(obj)
        self.categories = []
        self.relations = []
        self.relation_categories = []
        self.ancestors = 1
        self.offspring = 1
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        self.prepare_timeline_filters()
        self.timeline = Timeline(
            grstate.dbstate.db,
            events=self.categories,
            relatives=self.relations,
            relative_events=self.relation_categories,
        )
        if self.obj_type == "Person":
            self.timeline.set_person(
                obj.get_handle(),
                ancestors=self.ancestors,
                offspring=self.offspring,
            )
        elif self.obj_type == "Family":
            self.timeline.set_family(
                obj.get_handle(),
                ancestors=self.ancestors,
                offspring=self.offspring,
            )

        for event, event_ref, event_person, event_family, relation, category in self.timeline.events():
            event_frame = EventGrampsFrame(
                grstate,
                groptions,
                obj,
                event,
                event_ref,
                event_person,
                event_family,
                relation,
                category,
            )
            self.add_frame(event_frame)
        self.show_all()

    def prepare_timeline_filters(self):
        """
        Parse and prepare filter groups.
        """
        for category in EVENT_CATEGORIES:
            if self.get_option("show-class-{}".format(category)):
                self.categories.append(category)
            if self.obj_type == "Person":
                if self.get_option("show-family-class-{}".format(category)):
                    self.relation_categories.append(category)

        if self.obj_type == "Person":
            for relation in RELATIVES:
                if self.get_option("show-family-{}".format(relation)):
                    self.relations.append(relation)

        self.ancestors = self.get_option("generations-ancestors")
        self.offspring = self.get_option("generations-offspring")
