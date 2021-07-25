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
Media Profile Page
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
from frame_groups import (
    get_citations_group,
    get_notes_group,
    get_references_group,
)
from frame_image import ImageGrampsFrame
from frame_utils import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    ConfigReset,
    LayoutEditorButton
)
from page_base import BaseProfilePage

_ = glocale.translation.sgettext


class MediaProfilePage(BaseProfilePage):
    """
    Provides the media item profile page view with information about the media.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)

    def obj_type(self):
        return 'Media'

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, media):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not media:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "options.media", self.config
        )
        self.active_profile = ImageGrampsFrame(grstate, "active", media)

        groups = self.config.get("options.media.layout.groups").split(",")
        obj_groups = {}

        if "citation" in groups:
            obj_groups.update({"citation": get_citations_group(grstate, media)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, media)})
        if "reference" in groups:
            obj_groups.update({"reference": get_references_group(grstate, media)})

        body = self.render_group_view(obj_groups)
        if self.config.get("options.media.page.pinned-header"):
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
            grid, _("Pin active media header so it does not scroll"),
            11, "options.media.page.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            12, "options.media.page.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        editor = LayoutEditorButton(self.uistate, self.config, "Media")
        grid.attach(editor, 1, 19, 1, 1)
        reset = ConfigReset(configdialog, self.config, "options.media.page", label=_("Reset Page Defaults"))
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
            4, "options.media.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.media.active.tag-width",
            (1, 20)
        )
        reset = ConfigReset(configdialog, self.config, "options.media.active", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Media"), grid

    def sources_panel(self, configdialog):
        """
        Builds sources options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Image display mode"),
            1, "options.media.source.image-mode",
            IMAGE_DISPLAY_MODES,
        )        
        configdialog.add_combo(
            grid, _("Tag display mode"),
            2, "options.media.source.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            3, "options.media.source.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "options.media.source", 16, start_col=1, number=4, obj_type="Sources")
        reset = ConfigReset(configdialog, self.config, "options.media.source", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Sources"), grid

    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.page_panel,
            self.active_panel,
        ]
