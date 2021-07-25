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
from frame_base import GrampsState
from frame_groups import get_references_group
from frame_note import NoteGrampsFrame
from frame_utils import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    ConfigReset,
)
from page_base import BaseProfilePage

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
            "preferences.profile.note", self.config,
        )
        self.active_profile = NoteGrampsFrame(grstate, "active", note)

        groups = self.config.get("preferences.profile.note.layout.groups").split(",")
        obj_groups = {}

        if "reference" in groups:
            obj_groups.update({"reference": get_references_group(grstate, note)})

        body = self.render_group_view(obj_groups)
        if self.config.get("preferences.profile.note.page.pinned-header"):
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
        configdialog.add_text(grid, _("Page Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid, _("Pin active source header so it does not scroll"),
            2, "preferences.profile.note.page.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Use smaller font for detail attributes"),
            7, "preferences.profile.note.page.use-smaller-detail-font",
            tooltip=_("Enabling this option uses a smaller font for all the detailed information than used for the title.")
        )
        configdialog.add_spinner(
            grid, _("Desired border width"),
            8, "preferences.profile.note.page.border-width",
            (0, 5),
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            9, "preferences.profile.note.page.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Sort tags by name not priority"),
            11, "preferences.profile.note.page.sort-tags-by-name",
            tooltip=_("Enabling this option will sort tags by name before displaying them. By default they sort by the priority in which they are organized in the tag organization tool.")
        )
        configdialog.add_checkbox(
            grid, _("Enable warnings"),
            13, "preferences.profile.note.page.enable-warnings",
            tooltip=_("Enabling this will raise a warning dialog asking for confirmation before performing an action that removes or deletes data as a safeguard.")
        )
        configdialog.add_checkbox(
            grid, _("Enable tooltips"),
            14, "preferences.profile.note.page.enable-tooltips",
            tooltip=_("TBD TODO. If implemented some tooltips may be added to the view as an aid for new Gramps users which would quickly become annoying so this would turn them off for experienced users.")
        )
        reset = ConfigReset(configdialog, self.config, "preferences.profile.note.page", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Page"), grid

    def active_panel(self, configdialog):
        """
        Builds active note options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.note.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.note.active.tag-width",
            (1, 20)
        )
        reset = ConfigReset(configdialog, self.config, "preferences.profile.note.active", label=_("Reset Page Defaults"))
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
