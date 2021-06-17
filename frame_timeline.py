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
from gi.repository import Gtk, GdkPixbuf


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventType, Citation, Span
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsConfig
from frame_event import EventGrampsFrame
from timeline import EVENT_CATEGORIES, RELATIVES, Timeline
from frame_utils import get_relation, get_confidence, TextLink, get_key_person_events

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

    def __init__(self, dbstate, uistate, person, router, config=None, space="preferences.profile.person"):
        Gtk.VBox.__init__(self, expand=False, margin_right=3, margin_left=3, margin_top=0, margin_bottom=0, spacing=3)
        GrampsConfig.__init__(self, dbstate, uistate, space, config, router)
        self.count = 0
        self.categories = []
        self.relations = []
        self.ancestors = 1
        self.offspring = 1
        
        self.prepare_timeline_filters()
        self.timeline = Timeline(self.dbstate.db, events=self.categories, relatives=self.relations)
        self.timeline.add_person(person.handle, anchor=True, ancestors=self.ancestors, offspring=self.offspring)

        groups = {
            "age": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }    
        for timeline_event in self.timeline.events():
            event_frame = EventGrampsFrame(self.dbstate, self.uistate, self.space, self.config, router, person,
                                           timeline_event[0], timeline_event[1], timeline_event[2],
                                           groups=groups)
            self.pack_start(event_frame, False, False, 0)
            self.count = self.count + 1
        self.show_all()

    def prepare_timeline_filters(self):
        for category in EVENT_CATEGORIES:
            if self.config.get('{}.timeline.show-class-{}'.format(self.space, category)):
                self.categories.append(category)

        for relation in RELATIVES:
            if self.config.get('{}.timeline.show-family-{}'.format(self.space, relation)):
                self.relations.append(relation)
        self.ancestors = self.config.get('{}.timeline.generations-ancestors'.format(self.space))
        self.offspring = self.config.get('{}.timeline.generations-offspring'.format(self.space))
