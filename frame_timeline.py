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
from frame_event import EventGrampsFrame
from frame_list import GrampsFrameList
from frame_utils import get_gramps_object_type
from timeline import EVENT_CATEGORIES, RELATIVES, Timeline

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# TimelineGrampsFrameGroup
#
# ------------------------------------------------------------------------
class TimelineGrampsFrameGroup(GrampsFrameList):
    """
    The TimelineGrampsFrameGroup generates an event timeline for a person
    that may also optionally include events for close family if choosen.
    """

    def __init__(self, grstate, obj):
        GrampsFrameList.__init__(self, grstate)
        self.obj = obj
        self.obj_type, skip1, skip2 = get_gramps_object_type(obj)
        self.categories = []
        self.relations = []
        self.relation_categories = []
        self.ancestors = 1
        self.offspring = 1
        if not self.option("layout", "tabbed"):
            self.hideable = self.option("layout.timeline", "hideable")

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

        groups = {
            "age": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        for event, event_ref, event_person, event_family, relation, category in self.timeline.events():
            event_frame = EventGrampsFrame(
                grstate,
                "timeline",
                obj,
                event,
                event_ref,
                event_person,
                event_family,
                relation,
                category,
                groups=groups,
            )
            self.add_frame(event_frame)
        self.show_all()

    def prepare_timeline_filters(self):
        """
        Parse and prepare filter groups.
        """
        for category in EVENT_CATEGORIES:
            if self.option("timeline", "show-class-{}".format(category)):
                self.categories.append(category)
            if self.obj_type == "Person":
                if self.option("timeline", "show-family-class-{}".format(category)):
                    self.relation_categories.append(category)

        if self.obj_type == "Person":
            for relation in RELATIVES:
                if self.option("timeline", "show-family-{}".format(relation)):
                    self.relations.append(relation)

        self.ancestors = self.option("timeline", "generations-ancestors")
        self.offspring = self.option("timeline", "generations-offspring")
