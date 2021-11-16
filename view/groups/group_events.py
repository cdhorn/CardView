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
EventsGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import EventRef
from gramps.gui.editors import EditEventRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import get_gramps_object_type
from ..frames.frame_event_ref import EventRefGrampsFrame
from .group_list import GrampsFrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# EventsGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class EventsGrampsFrameGroup(GrampsFrameGroupList):
    """
    The EventsGrampsFrameGroup class provides a container for managing
    the events associated with an object like a person or family. It only
    manages the list directly associated with the object, unlike a timeline
    that will look for all events associated with an object.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(self, grstate, groptions)
        self.obj = obj
        self.obj_type = get_gramps_object_type(obj)
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        groptions.set_ref_mode(
            self.grstate.config.get("options.group.event.reference-mode")
        )
        groptions.set_relation(obj)
        for event_ref in obj.get_event_ref_list():
            event = self.grstate.fetch("Event", event_ref.ref)
            frame = EventRefGrampsFrame(
                grstate,
                groptions,
                event,
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
            for ref in self.obj.get_event_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
                    break
        action = "{} {} {} {} {}".format(
            _("Reordered"),
            _("Events"),
            _("for"),
            self.obj_type,
            self.obj.get_gramps_id(),
        )
        commit_method = self.grstate.dbstate.db.method(
            "commit_%s", self.obj_type
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.obj.set_event_ref_list(new_list)
            commit_method(self.obj, trans)

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
        callback = lambda x: self.save_new_event(x, insert_row)
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

    def save_new_event(self, event_ref, insert_row):
        """
        Save the new event added to the list of events.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.obj.get_event_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
        new_list.insert(insert_row, event_ref)
        event = self.fetch("Event", event_ref.ref)
        action = "{} {} {} {} {} {}".format(
            _("Added"),
            _("Event"),
            event.get_gramps_id(),
            _("to"),
            self.obj_type,
            self.obj.get_gramps_id(),
        )
        commit_method = self.grstate.dbstate.db.method(
            "commit_%s", self.obj_type
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.obj.set_event_ref_list(new_list)
            commit_method(self.obj, trans)
