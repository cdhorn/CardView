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
MediaRefCard
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
from ..actions import action_handler
from ..common.common_strings import (
    DELETE_REFERENCE,
    EDIT_REFERENCE,
    MAKE_MEDIA_ACTIVE,
)
from ..menus.menu_utils import menu_item
from .card_media import MediaCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaRefCard Class
#
# ------------------------------------------------------------------------
class MediaRefCard(MediaCard):
    """
    The MediaRefCard exposes the image and some facts about Media.
    """

    def __init__(self, grstate, groptions, obj, media_ref):
        media = grstate.fetch("Media", media_ref.ref)
        MediaCard.__init__(
            self, grstate, groptions, media, reference_tuple=(obj, media_ref)
        )

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for the reference.
        """
        action = action_handler(
            "Media", self.grstate, self.reference, self.reference_base
        )
        context_menu.append(
            menu_item("gtk-edit", EDIT_REFERENCE, action.edit_media)
        )
        if self.grstate.config.get("menu.delete"):
            context_menu.append(
                menu_item(
                    "list-remove",
                    DELETE_REFERENCE,
                    action.remove_media_reference,
                )
            )
        context_menu.append(
            menu_item(
                "gramps-media",
                MAKE_MEDIA_ACTIVE,
                action.set_active_media,
            )
        )
