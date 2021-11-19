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
AssociationsGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import PersonRef
from gramps.gui.editors import EditPersonRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_person_ref import PersonRefGrampsFrame
from ..frames.frame_person_backref import PersonBackRefGrampsFrame
from .group_list import GrampsFrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AssociationsGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class AssociationsGrampsFrameGroup(GrampsFrameGroupList):
    """
    The AssociationsGrampsFrameGroup class provides a container for managing
    all of the associations a person has with other people.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(self, grstate, groptions, obj)
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        groptions.set_ref_mode(
            self.grstate.config.get("options.group.association.reference-mode")
        )
        for person_ref in obj.get_person_ref_list():
            frame = PersonRefGrampsFrame(
                grstate,
                groptions,
                obj,
                person_ref,
            )
            self.add_frame(frame)

        obj_list = grstate.dbstate.db.find_backlink_handles(obj.get_handle())
        if obj_list:
            for item in obj_list:
                if item[0] == "Person":
                    person = grstate.fetch("Person", item[1])
                    for person_ref in person.get_person_ref_list():
                        if person_ref.ref == obj.get_handle():
                            frame = PersonBackRefGrampsFrame(
                                grstate,
                                groptions,
                                person,
                                person_ref,
                            )
                            self.add_frame(frame)
                            break
        self.show_all()

    def save_reordered_list(self):
        """
        Save a reordered list of associations.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_person_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
                    break
        message = "{} {} {} {} {}".format(
            _("Reordered"),
            _("Associations"),
            _("for"),
            _("Person"),
            self.group_base.obj.get_gramps_id(),
        )
        self.group_base.obj.set_person_ref_list(new_list)
        self.group_base.commit(self.grstate, message)

    def save_new_object(self, handle, insert_row):
        """
        Add a new person to the list of associations.
        """
        for frame in self.row_frames:
            if frame.primary.obj.get_handle() == handle:
                return

        person_ref = PersonRef()
        person_ref.ref = handle
        callback = lambda x: self.save_new_person(x, insert_row)
        try:
            EditPersonRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                person_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def save_new_person(self, person_ref, insert_row):
        """
        Save the new person added to the list of associations.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_person_ref_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
        new_list.insert(insert_row, person_ref)
        person = self.fetch("Person", person_ref.ref)
        message = "{} {} {} {} {} {} {}".format(
            _("Added"),
            _("Person"),
            person.get_gramps_id(),
            _("Association"),
            _("to"),
            _("Person"),
            self.group_base.obj.get_gramps_id(),
        )
        self.group_base.obj.set_person_ref_list(new_list)
        self.group_base.commit(self.grstate, message)
