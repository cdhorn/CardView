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
UrlCard
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
from html import escape

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.display import display_url
from gramps.gui.utils import match_primary_mask

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_const import BUTTON_PRIMARY
from ..common.common_utils import button_released
from .card_secondary import SecondaryCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# UrlCard Class
#
# ------------------------------------------------------------------------
class UrlCard(SecondaryCard):
    """
    The UrlCard exposes some of the basic facts about an Url.
    """

    def __init__(
        self,
        grstate,
        groptions,
        obj,
        url,
    ):
        SecondaryCard.__init__(self, grstate, groptions, obj, url)
        self.link = url.get_full_path()

        label = Gtk.Label(
            use_markup=True, label="<b>%s</b>" % escape(self.link)
        )
        self.widgets["title"].pack_start(label, False, False, 0)

        if url.get_description():
            self.add_fact(self.get_label(url.get_description()))

        if url.get_type():
            self.add_fact(self.get_label(str(url.get_type())))

        self.show_all()
        self.enable_drag()
        self.set_css_style()

    def cb_button_released(self, obj, event):
        """
        Handle button release.
        """
        if button_released(event, BUTTON_PRIMARY):
            if match_primary_mask(event.state):
                self._dump_context()
                return True
            display_url(self.link)
            return True
        return False
