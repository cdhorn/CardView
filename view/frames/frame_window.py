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
FrameDebugWindow
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import json

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
from gramps.gui.managedwindow import ManagedWindow

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------

_ = glocale.translation.sgettext


class FrameDebugWindow(ManagedWindow):
    """
    Window to display a serialized dump of the frame objects.
    """

    def __init__(self, grstate, grcontext):
        """
        Initialize class.
        """
        self.grstate = grstate
        self.grcontext = grcontext
        text = " ".join(
            (
                grcontext.primary_obj.obj_lang,
                grcontext.primary_obj.obj.get_gramps_id(),
            )
        )
        if grcontext.reference_obj:
            text = "".join((text, ": ", grcontext.reference_obj.obj_lang))
        if grcontext.secondary_obj:
            text = "".join((text, ": ", grcontext.secondary_obj.obj_lang))
        self.title = "".join((_("Frame Context Objects"), ": ", text))
        ManagedWindow.__init__(self, grstate.uistate, [], self.__class__)

        data = grcontext.serialize()
        text = json.dumps(json.loads(data), indent=4)
        text_buffer = Gtk.TextBuffer()
        text_buffer.set_text(text)
        text_view = Gtk.TextView.new_with_buffer(text_buffer)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(text_view)
        window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.uistate.window)
        window.add(scroll)
        self.set_window(window, None, self.title)
        self.setup_configs("interface.linked-view.debug", 768, 768)
        self.show()

    def build_window_key(self, _dummy_obj):
        """
        Return window key.
        """
        return "dump-window-key"

    def build_title(self, title):
        """
        Build title if one not provided.
        """
        return self.title

    def build_menu_names(self, _dummy_obj):
        """
        Build menu names.
        """
        return (self.title, None)
