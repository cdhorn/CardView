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

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


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

    def __init__(
        self,
        dbstate,
        uistate,
        router,
        obj,
        config=None,
        space="preferences.profile.person",
    ):
        GrampsFrameList.__init__(self, dbstate, uistate, space, config, router=router)
        self.obj = obj
        self.obj_type, skip1, skip2 = get_gramps_object_type(obj)
        self.count = 0
        self.categories = []
        self.relations = []
        self.relation_categories = []
        self.ancestors = 1
        self.offspring = 1

        self.prepare_timeline_filters()
        self.timeline = Timeline(
            self.dbstate.db, events=self.categories, relatives=self.relations, relative_events=self.relation_categories
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
                self.dbstate,
                self.uistate,
                self.space,
                self.config,
                router,
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
            self.count = self.count + 1
        self.show_all()

    def prepare_timeline_filters(self):
        """
        Parse and prepare filter groups.
        """
        for category in EVENT_CATEGORIES:
            if self.config.get(
                "{}.timeline.show-class-{}".format(self.space, category)
            ):
                self.categories.append(category)
            if self.obj_type == "Person":
                if self.config.get(
                        "{}.timeline.show-family-class-{}".format(self.space, category)
                ):
                    self.relation_categories.append(category)

        if self.obj_type == "Person":
            for relation in RELATIVES:
                if self.config.get(
                        "{}.timeline.show-family-{}".format(self.space, relation)
                ):
                    self.relations.append(relation)

        self.ancestors = self.config.get(
            "{}.timeline.generations-ancestors".format(self.space)
        )

        self.offspring = self.config.get(
            "{}.timeline.generations-offspring".format(self.space)
        )
