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
LDSOrdinanceFrame
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.db import family_name

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext
from .frame_secondary import SecondaryFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# LDSOrdinanceFrame Class
#
# ------------------------------------------------------------------------
class LDSOrdinanceFrame(SecondaryFrame):
    """
    The LDSOrdinanceFrame exposes the basic facts about an Ordinance.
    """

    def __init__(self, grstate, groptions, obj, ordinance):
        SecondaryFrame.__init__(self, grstate, groptions, obj, ordinance)
        self.__add_ordinance_title(ordinance)
        self.__add_ordinance_date(ordinance)
        self.__add_ordinance_place(ordinance)
        self.__add_ordinance_family(ordinance)
        self.__add_ordinance_temple(ordinance)
        self.__add_ordinance_status(ordinance)
        self.show_all()
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_ordinance_title(self, ordinance):
        """
        Add ordinance title.
        """
        title = ": ".join((_("LDS"), ordinance.type2str()))
        label = self.get_link(
            title,
            self.primary.obj,
            self.primary.obj.handle,
            callback=self.switch_ordinance_page,
        )
        self.widgets["title"].pack_start(label, False, False, 0)

    def __add_ordinance_date(self, ordinance):
        """
        Add ordinance date.
        """
        ordinance_date = ordinance.get_date_object()
        if ordinance_date:
            date = glocale.date_displayer.display(ordinance_date)
            if date:
                self.add_fact(
                    self.get_label(date), label=self.get_label(_("Date"))
                )
            age_base = self.groptions.age_base
            if age_base and (
                self.groptions.context in ["timeline"]
                or self.grstate.config.get("group.ldsord.show-age")
            ):
                self.load_age(age_base, ordinance_date)

    def __add_ordinance_place(self, ordinance):
        """
        Add ordinance place.
        """
        text = place_displayer.display_event(
            self.grstate.dbstate.db, ordinance
        )
        if text:
            place = self.get_link(
                text,
                "Place",
                ordinance.place,
                hexpand=False,
                title=False,
            )
            self.add_fact(place, label=self.get_label(_("Place")))

    def __add_ordinance_family(self, ordinance):
        """
        Add ordinance family.
        """
        ordinance_handle = ordinance.famc
        if ordinance_handle:
            family = self.grstate.fetch("Family", ordinance_handle)
            text = family_name(family, self.grstate.dbstate.db)
            self.add_fact(
                self.get_label(text), label=self.get_label(_("Family"))
            )

    def __add_ordinance_temple(self, ordinance):
        """
        Add ordinance temple.
        """
        temple = ordinance.temple
        if temple:
            self.add_fact(
                self.get_label(temple), label=self.get_label(_("Temple"))
            )

    def __add_ordinance_status(self, ordinance):
        """
        Add ordinance status.
        """
        if ordinance.status:
            self.add_fact(
                self.get_label(ordinance.status2str()),
                label=self.get_label(_("Status")),
            )

    def switch_ordinance_page(self, *_dummy_obj):
        """
        Initiate switch to ordinance page.
        """
        page_context = GrampsContext(
            self.primary.obj, None, self.secondary.obj
        )
        return self.grstate.load_page(page_context.pickled)
