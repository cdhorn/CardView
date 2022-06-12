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
PlaceAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Place, PlaceRef
from gramps.gui.editors import EditPlace, EditPlaceRef
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlaceAction Class
#
# ------------------------------------------------------------------------
class PlaceAction(GrampsAction):
    """
    Class to support actions related to places.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)

    def edit_place(self, *_dummy_args, focus=False, callback=None):
        """
        Edit the place.
        """
        if focus and callback is None:
            callback = lambda x: self.pivot_focus(x, "Place")
        try:
            EditPlace(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                callback,
            )
        except WindowActiveError:
            pass

    def _edit_place_reference(self, place, place_ref, callback=None):
        """
        Launch the place reference editor.
        """
        try:
            EditPlaceRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                place,
                place_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def add_new_enclosed_place(self, *_dummy_args):
        """
        Add a new enclosed place.
        """
        place = Place()
        place_ref = PlaceRef()
        place_ref.ref = self.action_object.obj.handle
        place.add_placeref(place_ref)
        self._edit_place_reference(
            place, place_ref, self._save_place_reference
        )

    def add_existing_enclosed_place(self, *_dummy_args):
        """
        Add an existing place as an enclosed place.
        """
        get_place_selector = SelectorFactory("Place")
        skip = [self.target_object.obj.handle]
        place_selector = get_place_selector(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        place = place_selector.run()
        if place:
            place_ref = PlaceRef()
            place_ref.ref = self.target_object.obj.handle
            place.add_placeref(place_ref)
            self._edit_place_reference(
                place, place_ref, self._save_place_reference
            )

    def _save_place_reference(self, place_ref, saved_place):
        """
        Update the place title if needed.
        """
        place = self.db.get_place_from_handle(saved_place.handle)
        if not place.title:
            place_name = place.get_name().get_value()
            if place_ref and place_ref.ref:
                top_place = self.db.get_place_from_handle(place_ref.ref)
                if top_place:
                    top_place_name = top_place.get_name().get_value()
                    if top_place_name:
                        place_name = "%s, %s" % (top_place_name, place_name)
            if place_name:
                message = _("Updating Place Title %s for %s") % (
                    place_name,
                    place.gramps_id,
                )
                self.grstate.uistate.set_busy_cursor(True)
                with DbTxn(message, self.db) as trans:
                    place.set_title(place_name)
                    self.db.commit_place(place, trans)
                self.grstate.uistate.set_busy_cursor(False)

    def remove_place_reference(self, *_dummy_args):
        """
        Remove an enclosed place reference.
        """
        if self.target_object.obj_type == "Place":
            place = self.target_object.obj
        elif self.target_object.obj_type == "PlaceRef":
            place = self.db.get_place_from_handle(self.target_object.obj.ref)

        place_name = place_displayer.display(self.db, place)
        enclosed_place_name = place_displayer.display(
            self.db, self.action_object.obj
        )
        message1 = _("Remove Enclosed Place %s?") % enclosed_place_name
        message2 = _(
            "Removing the enclosed place will remove the place reference "
            "from the enclosed place %s to the parent place %s in the "
            "database."
        ) % (enclosed_place_name, place_name)
        self.verify_action(
            message1,
            message2,
            _("Remove Place"),
            self._remove_place,
            recover_message=False,
        )

    def _remove_place(self, *_dummy_args):
        """
        Actually remove the enclosed place reference.
        """
        if self.target_object.obj_type == "Place":
            place_handle = self.target_object.obj.handle
        elif self.target_object.obj_type == "PlaceRef":
            place_handle = self.target_object.obj.ref

        new_list = []
        for place_ref in self.action_object.obj.placeref_list:
            if place_ref.ref != place_handle:
                new_list.append(place_ref)

        place_name = place_displayer.display(self.db, self.action_object.obj)
        message = _("Removed Enclosed Place %s from %s") % (
            place_name,
            self.describe_object(self.target_object.obj),
        )
        self.action_object.obj.set_placeref_list(new_list)
        self.action_object.commit(self.grstate, message)


factory.register_action("Place", PlaceAction)
