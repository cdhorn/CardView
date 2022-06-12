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
NoteCard
"""

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
from gramps.gen.lib import StyledText
from gramps.gui.widgets import StyledTextBuffer

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..menus.menu_utils import menu_item
from .card_primary import PrimaryCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# NoteCard Class
#
# ------------------------------------------------------------------------
class NoteCard(PrimaryCard):
    """
    The NoteCard exposes some of the basic facts about a Note.
    """

    def __init__(self, grstate, groptions, note, reference=None):
        self.text_view = Gtk.TextView(
            wrap_mode=Gtk.WrapMode.WORD, editable=False, cursor_visible=False
        )
        PrimaryCard.__init__(self, grstate, groptions, note)
        self.note_reference = reference
        preview_mode = self.get_option("preview-mode")
        preview_lines = self.get_option("preview-lines")
        self.__add_note_text(note, preview_mode, preview_lines)
        self.__add_note_title(note, preview_mode)
        self.__add_note_reference(reference)
        self.enable_drag()
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_note_text(self, note, preview_mode, preview_lines):
        """
        Add note text.
        """
        styled_text_buffer = StyledTextBuffer()
        text = note.get_styledtext()
        if preview_mode:
            lines = text.split("\n")[:preview_lines]
            new_lines = []
            count = 1
            last = len(lines)
            for line in lines:
                new_text = StyledText()
                if count != last:
                    new_text = new_text.join([line, "\n"])
                else:
                    new_text = line
                new_lines.append(new_text)
                count = count + 1
            text = StyledText()
            text = text.join(new_lines)
        styled_text_buffer.set_text(text)
        self.text_view.set_buffer(styled_text_buffer)

    def __add_note_title(self, note, preview_mode):
        """
        Add note title.
        """
        title = ""
        if note.type:
            title = glocale.translation.sgettext(note.type.xml_str())
        if preview_mode:
            if title:
                title = "%s (%s)" % (title, _("Preview"))
            else:
                title = _("Preview")
        if title:
            label = self.get_link(
                title,
                "Note",
                note.handle,
            )
            self.add_fact(label)

    def __add_note_reference(self, reference):
        """
        Add note reference.
        """
        if reference:
            self.widgets["attributes"].add_fact(self.get_label(reference))

    def build_layout(self):
        """
        Construct framework for note layout, overrides base class.
        """
        vcontent = Gtk.VBox(spacing=3)
        self.widgets["body"].pack_start(
            vcontent, expand=True, fill=True, padding=0
        )

        hcontent = Gtk.HBox(hexpand=True)
        vfacts = Gtk.VBox(vexpand=False, hexpand=True)
        vfacts.pack_start(
            self.widgets["facts"], expand=True, fill=True, padding=0
        )
        vfacts.pack_start(
            self.widgets["icons"], expand=True, fill=True, padding=0
        )
        hcontent.pack_start(vfacts, expand=True, fill=True, padding=0)

        vmeta = Gtk.VBox(vexpand=False, hexpand=False)
        vmeta.pack_start(self.widgets["id"], expand=True, fill=True, padding=0)
        vmeta.pack_start(
            self.widgets["attributes"], expand=True, fill=True, padding=0
        )
        hcontent.pack_start(vmeta, expand=True, fill=True, padding=0)

        if self.get_option("text-on-top"):
            vcontent.pack_start(
                self.text_view, expand=True, fill=True, padding=0
            )
            vcontent.pack_start(hcontent, expand=True, fill=True, padding=0)
        else:
            vcontent.pack_start(hcontent, expand=True, fill=True, padding=0)
            vcontent.pack_start(
                self.text_view, expand=True, fill=True, padding=0
            )

    def add_custom_actions(self, context_menu):
        """
        Add action menu items for the note.
        """
        if self.groptions.backlink:
            (obj_type, obj_handle) = self.groptions.backlink
            obj = self.fetch(obj_type, obj_handle)
            action = action_handler("Note", self.grstate, self.primary, obj)
            context_menu.append(
                menu_item(
                    "list-remove",
                    _("Remove note"),
                    action.remove_note,
                )
            )
