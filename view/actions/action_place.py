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
PlaceAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
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
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlaceAction class
#
# ------------------------------------------------------------------------
class PlaceAction(GrampsAction):
    """
    Class to support actions related to places.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)

    def edit_place(self, *_dummy_args):
        """
        Edit the place.
        """
        try:
            EditPlace(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
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
        place_ref.ref = self.action_object.obj.get_handle()
        place.add_placeref(place_ref)
        self._edit_place_reference(
            place, place_ref, self._save_place_reference
        )

    def add_existing_enclosed_place(self, *_dummy_args):
        """
        Add an existing place as an enclosed place.
        """
        get_place_selector = SelectorFactory("Place")
        skip = [self.action_object.obj.get_handle()]
        place_selector = get_place_selector(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        place = place_selector.run()
        if place:
            place_ref = PlaceRef()
            place_ref.ref = self.action_object.obj.get_handle()
            place.add_placeref(place_ref)
            self._edit_place_reference(
                place, place_ref, self._save_place_reference
            )

    def _save_place_reference(self, place_ref, saved_place):
        """
        Update the place title if needed.
        """
        place = self.db.get_place_from_handle(saved_place.get_handle())
        if not place.get_title():
            place_name = place.get_name().get_value()
            if place_ref and place_ref.ref:
                top_place = self.db.get_place_from_handle(place_ref.ref)
                if top_place:
                    top_place_name = top_place.get_name().get_value()
                    if top_place_name:
                        place_name = ", ".join((top_place_name, place_name))
            if place_name:
                message = " ".join(
                    (
                        _("Updating"),
                        _("Place"),
                        _("Title"),
                        place_name,
                        _("for"),
                        place.get_gramps_id(),
                    )
                )
                with DbTxn(message, self.db) as trans:
                    place.set_title(place_name)
                    self.db.commit_place(place, trans)

    def remove_place_reference(self, *_dummy_args):
        """
        Remove an enclosed place reference.
        """
        if self.target_object.obj_type == "Place":
            place = self.target_object.obj
        elif self.target_object.obj_type == "PlaceRef":
            place = self.db.get_place_from_handle(self.target_object.obj.ref)
        text = place_displayer.display(self.db, place)
        prefix = _(
            "You are about to remove the following enclosed place from this "
            "place:"
        )
        extra = _(
            "Note this does not delete the place. You can also use the "
            "undo option under edit if you change your mind later."
        )
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            new_list = []
            for place_ref in place.get_placeref_list():
                if not place_ref.ref == self.action_object.obj.get_handle():
                    new_list.append(place_ref)
            message = " ".join(
                (
                    _("Removed"),
                    _("PlaceRef"),
                    place.get_gramps_id(),
                    _("from"),
                    _("Place"),
                    self.action_object.obj.get_gramps_id(),
                )
            )
            with DbTxn(message, self.db) as trans:
                place.set_placeref_list(new_list)
                self.db.commit_place(place, trans)


factory.register_action("Place", PlaceAction)
