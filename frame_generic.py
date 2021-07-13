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
from gramps.gen.db import DbTxn


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_event import EventGrampsFrame
from frame_list import GrampsFrameList
from frame_person import PersonGrampsFrame
from frame_couple import CoupleGrampsFrame
from frame_utils import get_gramps_object_type

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# GenericGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class GenericGrampsFrameGroup(GrampsFrameList):
    """
    The GenericGrampsFrameGroup class provides a container for managing a
    set of generic frames for a list of primary Gramps objects.
    """

    def __init__(self, dbstate, uistate, router, space, config, obj_type, obj_handles, defaults=None):
        GrampsFrameList.__init__(self, dbstate, uistate, space, config, router=router)
        self.defaults = defaults
        self.obj_type = obj_type
        self.obj_handles = obj_handles

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        if obj_type == "Person":
            for handle in obj_handles:
                person = self.dbstate.db.get_person_from_handle(handle)
                frame = PersonGrampsFrame(
                    self.dbstate,
                    self.uistate,
                    person,
                    "people",
                    self.space,
                    self.config,
                    self.router,
                    groups=groups,
                    defaults=self.defaults
                )
                self.add_frame(frame)

        if obj_type == "Family":
            for handle in obj_handles:
                family = dbstate.db.get_family_from_handle(handle)
                frame = CoupleGrampsFrame(
                    self.dbstate,
                    self.uistate,
                    self.router,
                    family,
                    "family",
                    self.space,
                    self.config,
                    defaults=self.defaults
                )
                self.add_frame(frame)

        if obj_type == "Event":
            for handle in obj_handles:
                event = self.dbstate.db.get_event_from_handle(handle)
                frame = EventGrampsFrame(
                    self.dbstate,
                    self.uistate,
                    self.space,
                    self.config,
                    self.router,
                    None,
                    event,
                    None,
                    None,
                    None,
                    None,
                    "events"
                )
                self.add_frame(frame)

        self.show_all()
