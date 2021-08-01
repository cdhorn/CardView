# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
Note Profile Page
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk


# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames.frame_classes import GrampsState
from ..frames.frame_const import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
)    
from ..frames.frame_note import NoteGrampsFrame
from ..frames.frame_utils import (
    ConfigReset,
    LayoutEditorButton
)
from ..groups.group_utils import get_references_group
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class NoteProfilePage(BaseProfilePage):
    """
    Provides the note profile page view with information about the note.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)

    def obj_type(self):
        return 'Note'

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, note):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not note:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "options.note", self.config,
        )
        self.active_profile = NoteGrampsFrame(grstate, "active", note)

        groups = self.config.get("options.note.layout.groups").split(",")
        obj_groups = {}

        if "reference" in groups:
            obj_groups.update({"reference": get_references_group(grstate, note)})

        body = self.render_group_view(obj_groups)
        if self.config.get("options.note.page.pinned-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
        return True

    def page_panel(self, configdialog):
        """
        Builds page and styling options section for the configuration dialog
        """
        grid = self.create_grid()
        self._config_global_options(configdialog, grid, 0)
        configdialog.add_text(grid, _("Page Options"), 10, bold=True)
        configdialog.add_checkbox(
            grid, _("Pin active source header so it does not scroll"),
            11, "options.note.page.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            12, "options.note.page.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        editor = LayoutEditorButton(self.uistate, self.config, "Note")
        grid.attach(editor, 1, 19, 1, 1)
        reset = ConfigReset(configdialog, self.config, "options.note.page", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Page"), grid

    def active_panel(self, configdialog):
        """
        Builds active note options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid, _("Enable preview mode"),
            1, "options.note.active.preview-mode",
            tooltip=_("Indicates only a portion of the full note should be displayed.")
        )
        configdialog.add_spinner(
            grid, _("Number of lines to preview"),
            2, "options.note.active.preview-lines",
            (0, 8),
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            3, "options.note.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            4, "options.note.active.tag-width",
            (1, 20)
        )
        reset = ConfigReset(configdialog, self.config, "options.note.active", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Note"), grid

    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.page_panel,
            self.active_panel,
        ]
