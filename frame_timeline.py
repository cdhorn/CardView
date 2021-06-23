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
from frame_base import GrampsConfig
from frame_event import EventGrampsFrame
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
class TimelineGrampsFrameGroup(Gtk.VBox, GrampsConfig):
    """
    The TimelineGrampsFrameGroup generates an event timeline for a person
    that may also optionally include events for close family if choosen.
    """

    def __init__(
        self,
        dbstate,
        uistate,
        person,
        router,
        config=None,
        space="preferences.profile.person",
    ):
        Gtk.VBox.__init__(
            self,
            expand=False,
            margin_right=3,
            margin_left=3,
            margin_top=0,
            margin_bottom=0,
            spacing=3,
        )
        GrampsConfig.__init__(self, dbstate, uistate, space, config)
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
        self.timeline.set_person(
            person.handle,
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
                person,
                event,
                event_ref,
                event_person,
                event_family,
                relation,
                category,
                groups=groups,
            )
            self.pack_start(event_frame, False, False, 0)
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
            if self.config.get(
                "{}.timeline.show-family-class-{}".format(self.space, category)
            ):
                self.relation_categories.append(category)

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
