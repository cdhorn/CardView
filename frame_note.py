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
NoteGrampsFrame
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
from gramps.gui.widgets import StyledTextBuffer


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_class import GrampsFrame
from frame_utils import TextLink


# ------------------------------------------------------------------------
#
# NoteGrampsFrame Class
#
# ------------------------------------------------------------------------
class NoteGrampsFrame(GrampsFrame):
    """
    The NoteGrampsFrame exposes some of the basic facts about a Note.
    """

    def __init__(self, grstate, context, note, groups=None):
        self.text_view = Gtk.TextView(wrap_mode=Gtk.WrapMode.WORD, editable=False, cursor_visible=False)
        GrampsFrame.__init__(self, grstate, context, note, groups=groups)

        styled_text_buffer = StyledTextBuffer()
        styled_text_buffer.set_text(note.get_styledtext())
        self.text_view.set_buffer(styled_text_buffer)

        if note.type:
            text = glocale.translation.sgettext(note.type.xml_str())
            if text:
                self.add_fact(self.make_label(text))

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def build_layout(self):
        """
        Construct framework for note layout, overrides base class.
        """
        vcontent = Gtk.VBox(spacing=3)
        self.body.pack_start(vcontent, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.text_view, expand=True, fill=True, padding=0)
        hcontent = Gtk.HBox(hexpand=True)
        hcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        hcontent.pack_start(self.metadata, expand=True, fill=True, padding=0)
        vcontent.pack_start(hcontent, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.tags, expand=True, fill=True, padding=0)

