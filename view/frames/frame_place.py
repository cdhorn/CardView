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
PlaceGrampsFrame
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
from gramps.gen.db import DbTxn
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Place, PlaceRef
from gramps.gui.editors import EditPlaceRef
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_reference import ReferenceGrampsFrame
from ..common.common_utils import menu_item

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PlaceGrampsFrame Class
#
# ------------------------------------------------------------------------
class PlaceGrampsFrame(ReferenceGrampsFrame):
    """
    The PlaceGrampsFrame exposes some of the basic facts about a Place.
    """

    def __init__(self, grstate, groptions, place, reference_tuple=None):
        ReferenceGrampsFrame.__init__(
            self, grstate, groptions, place, reference_tuple=reference_tuple
        )

        if "group" in groptions.option_space:
            place_name = place_displayer.display(grstate.dbstate.db, place)
            title = self.get_link(
                place_name,
                "Place",
                place.get_handle(),
            )
        else:
            title = self.get_title_breadcrumbs()
        self.widgets["title"].pack_start(title, True, False, 0)

        if place.get_type():
            text = glocale.translation.sgettext(place.get_type().xml_str())
            if text:
                self.add_fact(
                    self.get_label(text), label=self.get_label(_("Type"))
                )
        if place.get_code():
            self.add_fact(
                self.get_label(place.get_code()),
                label=self.get_label(_("Code")),
            )

        if place.get_latitude():
            latitude_text = place.get_latitude()
        else:
            latitude_text = "".join(("[", _("Missing"), "]"))

        if place.get_longitude():
            longitude_text = place.get_longitude()
        else:
            longitude_text = "".join(("[", _("Missing"), "]"))
        text = ", ".join((latitude_text, longitude_text))
        label = ", ".join((_("Latitude"), _("Longitude")))
        self.add_fact(self.get_label(text), label=self.get_label(label))

        if place.get_alternative_names():
            for alternate_name in place.get_alternative_names():
                value = alternate_name.get_value()
                if alternate_name.get_language():
                    value = "".join(
                        (value, " (", alternate_name.get_language(), ")")
                    )

                date = glocale.date_displayer.display(
                    alternate_name.get_date_object()
                )
                if not date:
                    date = ""
                date = "  ".join((_("Alternate Name"), date))
                self.add_fact(
                    self.get_label(value),
                    label=self.get_label(date),
                    extra=True,
                )

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def get_title_breadcrumbs(self):
        """
        Return a title widget with linkable parts.
        """
        hbox = Gtk.HBox(hexpand=False, vexpand=False)
        chain = [self.primary.obj]
        self.get_place_chain(chain, self.primary.obj)
        comma_label = None
        for place in chain:
            title = place.get_name().get_value()
            if place.get_type():
                place_type = glocale.translation.sgettext(
                    place.get_type().xml_str()
                )
            else:
                place_type = None
            place_label = self.get_link(
                title, "Place", place.get_handle(), tooltip=place_type
            )
            if comma_label:
                hbox.pack_start(self.get_label(", "), False, False, 0)
            hbox.pack_start(place_label, False, False, 0)
            comma_label = True
        return hbox

    def get_place_chain(self, chain, obj):
        """
        Return list of parent places.
        """
        if obj.get_placeref_list():
            place_ref = obj.get_placeref_list()[0]
            place = self.grstate.fetch("Place", place_ref.ref)
            chain.append(place)
            self.get_place_chain(chain, place)

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def add_custom_actions(self, context_menu):
        """
        Add context menu items unique to a place.
        """
        context_menu.append(
            menu_item(
                "gramps-place",
                _("Add a new enclosed place"),
                self.add_new_enclosed_place,
            )
        )
        context_menu.append(
            menu_item(
                "gramps-place",
                _("Add an existing enclosed place"),
                self.add_existing_enclosed_place,
            )
        )

    def add_new_enclosed_place(self, *_dummy_args):
        """
        Add a new enclosed place.
        """
        place = Place()
        place_ref = PlaceRef()
        place_ref.ref = self.primary.obj.get_handle()
        place.add_placeref(place_ref)
        try:
            EditPlaceRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                place,
                place_ref,
                self.save_place_ref,
            )
        except WindowActiveError:
            pass

    def add_existing_enclosed_place(self, *_dummy_args):
        """
        Add an existing place as an enclosed place.
        """
        select_place = SelectorFactory("Place")
        skip = set([self.primary.obj.get_handle()])
        dialog = select_place(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        place = dialog.run()
        if place:
            place_ref = PlaceRef()
            place_ref.ref = self.primary.obj.get_handle()
            place.add_placeref(place_ref)
            try:
                EditPlaceRef(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    place,
                    place_ref,
                    self.save_place_ref,
                )
            except WindowActiveError:
                pass

    def save_place_ref(self, place_ref, saved_place):
        """
        Update the place title if needed.
        """
        place = self.grstate.dbstate.db.get_place_from_handle(
            saved_place.get_handle()
        )
        if not place.get_title():
            place_name = place.get_name().get_value()
            if place_ref and place_ref.ref:
                top_place = self.grstate.fetch("Place", place_ref.ref)
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
                with DbTxn(message, self.grstate.dbstate.db) as trans:
                    place.set_title(place_name)
                    self.grstate.dbstate.db.commit_place(place, trans)
