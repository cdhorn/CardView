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
EventsFrameGroup
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import EventRef, EventType
from gramps.gui.editors import EditEventRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames import EventRefFrame
from .group_list import FrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventsFrameGroup class
#
# ------------------------------------------------------------------------
class EventsFrameGroup(FrameGroupList):
    """
    The EventsFrameGroup class provides a container for managing
    the events associated with an object like a person or family. It only
    manages the list directly associated with the object, unlike a timeline
    that will look for all events associated with an object.
    """

    def __init__(self, grstate, groptions, obj):
        FrameGroupList.__init__(self, grstate, groptions, obj)
        if self.group_base.obj_type == "Person":
            self.birth_ref = self.group_base.obj.get_birth_ref()
            self.death_ref = self.group_base.obj.get_death_ref()
        else:
            self.birth_ref = None
            self.death_ref = None

        groptions.set_ref_mode(
            self.grstate.config.get("group.event.reference-mode")
        )
        groptions.set_relation(obj)

        for event_ref in obj.get_event_ref_list():
            frame = EventRefFrame(
                grstate,
                groptions,
                obj,
                event_ref,
            )
            self.add_frame(frame)
        self.show_all()

    def save_reordered_list(self):
        """
        Save a reordered list of events.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_event_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
                    break
        message = " ".join(
            (
                _("Reordered"),
                _("Events"),
                _("for"),
                self.group_base.obj_type,
                self.group_base.obj.get_gramps_id(),
            )
        )
        self.group_base.obj.set_event_ref_list(new_list)
        if self.birth_ref is not None:
            self.group_base.obj.set_birth_ref(self.birth_ref)
        if self.death_ref is not None:
            self.group_base.obj.set_death_ref(self.death_ref)
        self.group_base.commit(self.grstate, message)

    def save_new_object(self, handle, insert_row):
        """
        Add a new event to the list of events.
        """
        for frame in self.row_frames:
            if frame.primary.obj.get_handle() == handle:
                return

        event_ref = EventRef()
        event_ref.ref = handle
        event = self.grstate.fetch("Event", handle)
        callback = lambda x, y: self.save_new_event(x, y, insert_row)
        try:
            EditEventRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                event,
                event_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def save_new_event(self, event_ref, event, insert_row):
        """
        Save the new event added to the list of events.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_event_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
        new_list.insert(insert_row, event_ref)
        message = " ".join(
            (
                _("Added"),
                _("Event"),
                event.get_gramps_id(),
                _("to"),
                self.group_base.obj_type,
                self.group_base.obj.get_gramps_id(),
            )
        )
        if event.get_type == EventType.BIRTH and self.birth_ref:
            self.birth_ref = event_ref
        if event.get_type == EventType.DEATH and self.death_ref:
            self.death_ref = event_ref
        self.group_base.obj.set_event_ref_list(new_list)
        if self.birth_ref is not None:
            self.group_base.obj.set_birth_ref(self.birth_ref)
        if self.death_ref is not None:
            self.group_base.obj.set_death_ref(self.death_ref)
        self.group_base.commit(self.grstate, message)
