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
AddressCard
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import format_address
from .card_secondary import SecondaryCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AddressCard Class
#
# ------------------------------------------------------------------------
class AddressCard(SecondaryCard):
    """
    The AddressCard exposes some of the basic facts about an Address.
    """

    def __init__(
        self,
        grstate,
        groptions,
        obj,
        address,
    ):
        SecondaryCard.__init__(self, grstate, groptions, obj, address)
        self.__add_address_formatted(address)
        self.__add_address_phone(address)
        self.__add_address_date(address)
        if len(self.widgets["facts"]) == 0:
            self.add_fact(self.get_label("[%s]" % _("Empty")))
        self.show_all()
        self.enable_drag()
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_address_formatted(self, address):
        """
        Add formatted address.
        """
        lines = format_address(address)
        for line in lines:
            self.add_fact(self.get_label(line))

    def __add_address_phone(self, address):
        """
        Add phone number.
        """
        if address.phone:
            self.add_fact(self.get_label(address.phone))

    def __add_address_date(self, address):
        """
        Add address date.
        """
        address_date = address.get_date_object()
        if address_date:
            self.add_fact(
                self.get_label(glocale.date_displayer.display(address_date))
            )
            if self.groptions.age_base and (
                self.groptions.context in ["timeline"]
                or self.grstate.config.get("group.address.show-age")
            ):
                self.load_age(self.groptions.age_base, address_date)
