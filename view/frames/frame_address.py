#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021       Christopher Horn
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
AddressGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_secondary import SecondaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# AddressGrampsFrame class
#
# ------------------------------------------------------------------------
class AddressGrampsFrame(SecondaryGrampsFrame):
    """
    The AddressGrampsFrame exposes some of the basic facts about an Address.
    """

    def __init__(
        self,
        grstate,
        groptions,
        obj,
        address,
    ):
        SecondaryGrampsFrame.__init__(
            self, grstate, groptions, obj, address
        )
        if address.street:
            self.add_fact(self.make_label(address.street))
        if address.locality:
            self.add_fact(self.make_label(address.locality))
        if address.county:
            self.add_fact(self.make_label(address.county))
        if address.city:
            self.add_fact(self.make_label(address.city))
        if address.state:
            self.add_fact(self.make_label(address.state))
        if address.country:
            self.add_fact(self.make_label(address.country))
        if address.postal:
            self.add_fact(self.make_label(address.postal))
        if address.phone:
            self.add_fact(self.make_label(address.phone))
        if address.get_date_object():
            text = glocale.date_displayer.display(address.get_date_object())
            if text:
                self.add_fact(self.make_label(text))
        if len(self.facts_grid) == 0:
            self.add_fact(self.make_label("[{}]".format(_("Empty"))))
        self.show_all()
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()
