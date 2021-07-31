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
Event Profile Page
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
from frame_classes import GrampsState
from frame_const import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
)    
from frame_event import EventGrampsFrame
from frame_generic import GenericGrampsFrameGroup
from frame_groups import (
    get_citations_group,
    get_media_group,
    get_notes_group,
    get_references_group
)
from frame_utils import (
    ConfigReset,
    LayoutEditorButton
)
from page_base import BaseProfilePage

_ = glocale.translation.sgettext


class EventProfilePage(BaseProfilePage):
    """
    Provides the event profile page view with information about the event.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)

    def obj_type(self):
        return 'Event'

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, event):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not event:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "options.event", self.config,
        )
        self.active_profile = EventGrampsFrame(
            grstate,
            "active",
            None,
            event,
            None,
            None,
            None,
            None,
        )

        groups = self.config.get("options.event.layout.groups").split(",")
        obj_groups = {}

        if "citation" in groups:
            obj_groups.update({"citation": get_citations_group(grstate, event)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, event)})
        if "media" in groups:
            obj_groups.update({"media": get_media_group(grstate, event)})

        people_list = []
        family_list = []
        if "people" in groups or "family" in groups:
            for obj_type, obj_handle in self.dbstate.db.find_backlink_handles(event.get_handle()):
                if obj_type == "Person" and obj_handle not in people_list:
                    people_list.append(("Person", obj_handle))
                elif obj_type == "Family" and obj_handle not in family_list:
                    family_list.append(("Family", obj_handle))

        if people_list:
            obj_groups.update(
                {"people": get_references_group(
                    grstate, None,
                    title_plural=_("Individual Participants"),
                    title_single=_("Individial Participants"),
                    obj_list=people_list)
                 }
            )
        if family_list:
            obj_groups.update(
                {"family": get_references_group(
                    grstate, None,
                    title_plural=_("Family Participants"),
                    title_single=_("Family Participants"),
                    obj_list=family_list)
                 }
            )

        body = self.render_group_view(obj_groups)
        if self.config.get("options.event.page.pinned-header"):
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
            11, "options.event.page.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            12, "options.event.page.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Include notes on child objects"),
            13, "options.event.page.include-child-notes",
            tooltip=_("Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present.")
        )
        editor = LayoutEditorButton(self.uistate, self.config, "Event")
        grid.attach(editor, 1, 19, 1, 1)        
        reset = ConfigReset(configdialog, self.config, "options.event.page", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Page"), grid

    def active_panel(self, configdialog):
        """
        Builds active event options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.event.active.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.event.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.event.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.event.active.tag-width",
            (1, 20)
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=1, bold=True)
        self._config_metadata_attributes(grid, "options.event.active", 12, start_col=1, number=4, obj_type="Event")
        reset = ConfigReset(configdialog, self.config, "options.event.active", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Event"), grid

    def people_panel(self, configdialog):
        """
        Builds people options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.event.people.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.event.people.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.event.people.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.event.people.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.event.people.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.event.people.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.event.people", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.event.people", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.event.people", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("People"), grid

    def family_panel(self, configdialog):
        """
        Builds family options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.event.family.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.event.family.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.event.family.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.event.family.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=1, bold=True)
        self._config_metadata_attributes(grid, "options.event.family", 12, start_col=1, number=4, obj_type="Family")
        reset = ConfigReset(configdialog, self.config, "options.event.family", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Family"), grid

    def media_panel(self, configdialog):
        """
        Builds media options section for configuration dialog
        """
        return self._media_panel(configdialog, "options.event")

    def notes_panel(self, configdialog):
        """
        Builds notes options section for configuration dialog
        """
        return self._notes_panel(configdialog, "options.event")

    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.page_panel,
            self.active_panel,
            self.people_panel,
            self.family_panel,
            self.notes_panel,
            self.media_panel,
        ]
