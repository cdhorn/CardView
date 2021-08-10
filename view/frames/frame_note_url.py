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


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_base import GrampsFrame
from .frame_const import _LEFT_BUTTON, _RIGHT_BUTTON
from .frame_utils import (
    button_activated,
    TextLink
)

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

        vcontent = Gtk.VBox()
        self.title = Gtk.HBox(spacing=6)
        vcontent.pack_start(self.title, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        body = Gtk.HBox(hexpand=True, margin=3)
        body.pack_start(vcontent, expand=True, fill=True, padding=0)
        self.frame.add(body)
        self.eventbox.add(self.frame)
        self.add(self.eventbox)

        label = Gtk.Label(use_markup=True, label="<b>{}</b>".format(link))
        self.title.pack_start(label, False, False, 0)
        text = "{} {} {}".format(_("Found in"), _("Note"), note.get_gramps_id())
        note_link = TextLink(
            text,
            "Note",
            note.get_handle(),
            self.switch_object,
            hexpand=False,
            bold=False,
            markup=self.markup
        )
        self.facts_grid.attach(note_link, 0, 0, 1, 1)
        self.set_css_style()
        self.show_all()
        
    def route_action(self, obj, event):
        """
        Route the action if the frame was clicked on.
        """
        if not button_activated(event, _LEFT_BUTTON):
            if not button_activated(event, _RIGHT_BUTTON):
                display_url(self.link)
