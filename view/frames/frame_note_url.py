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
NoteUrlGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from html import escape

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
from gramps.gui.display import display_url

from ..common.common_const import BUTTON_PRIMARY
from ..common.common_utils import TextLink, button_released

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_base import GrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# NoteUrlGrampsFrame class
#
# ------------------------------------------------------------------------
class NoteUrlGrampsFrame(GrampsFrame):
    """
    The NoteUrlGrampsFrame class exposes information about a Url found
    in a Note record.
    """

    def __init__(self, grstate, groptions, note, link):
        GrampsFrame.__init__(self, grstate, groptions, note)
        self.link = link
        self.build_layout()

        label = Gtk.Label(
            use_markup=True, label="".join(("<b>", escape(link), "</b>"))
        )
        self.widgets["title"].pack_start(label, False, False, 0)
        text = " ".join((_("Found"), _("in"), _("note"), note.get_gramps_id()))
        note_link = TextLink(
            text,
            "Note",
            note.get_handle(),
            self.switch_object,
            hexpand=False,
            bold=False,
            markup=self.markup,
        )
        self.widgets["facts"].attach(note_link, 0, 0, 1, 1)
        self.set_css_style()
        self.show_all()

    def button_released(self, _dummy_obj, event):
        """
        Handle button released.
        """
        if button_released(event, BUTTON_PRIMARY):
            display_url(self.link)
            return True
        return False
