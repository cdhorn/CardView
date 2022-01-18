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
MediaRefFrame
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
from ..actions import action_handler
from ..menus.menu_utils import menu_item
from .frame_media import MediaFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaRefFrame Class
#
# ------------------------------------------------------------------------
class MediaRefFrame(MediaFrame):
    """
    The MediaRefFrame exposes the image and some facts about Media.
    """

    def __init__(self, grstate, groptions, obj, media_ref):
        media = grstate.fetch("Media", media_ref.ref)
        MediaFrame.__init__(
            self, grstate, groptions, media, reference_tuple=(obj, media_ref)
        )

    def add_ref_custom_actions(self, context_menu):
        """
        Add custom action menu items for the reference.
        """
        action = action_handler(
            "Media", self.grstate, self.reference, self.reference_base
        )
        label = " ".join((_("Edit"), _("reference")))
        context_menu.append(menu_item("gtk-edit", label, action.edit_media))
        if self.grstate.config.get("menu.delete"):
            label = " ".join((_("Delete"), _("reference")))
            context_menu.append(
                menu_item("list-remove", label, action.remove_media_reference)
            )
        context_menu.append(
            menu_item(
                "gramps-media",
                _("Make active media"),
                action.set_active_media,
            )
        )
