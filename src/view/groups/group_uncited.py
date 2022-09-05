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
UncitedEventsCardGroup
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
from ..cards import EventRefCard
from .group_list import CardGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# UncitedEventsCardGroup Class
#
# ------------------------------------------------------------------------
class UncitedEventsCardGroup(CardGroupList):
    """
    The UncitedEventsCardGroup class provides a container for displaying
    events associated with an object that have no citations.
    """

    def __init__(self, grstate, groptions, obj):
        CardGroupList.__init__(self, grstate, groptions, obj)

        groptions.set_ref_mode(
            self.grstate.config.get("group.event.reference-mode")
        )
        groptions.set_relation(obj)

        db = self.grstate.dbstate.db
        for event_ref in obj.event_ref_list:
            event = db.get_event_from_handle(event_ref.ref)
            if not event.citation_list:
                card = EventRefCard(
                    grstate,
                    groptions,
                    obj,
                    event_ref,
                )
                self.add_card(card)
        self.show_all()
