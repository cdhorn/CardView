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
Citation Profile Page
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
from frame_citation import CitationGrampsFrame
from frame_generic import GenericGrampsFrameGroup
from frame_groups import (
    get_citations_group,
    get_media_group,
    get_notes_group,
    get_repositories_group
)
from frame_source import SourceGrampsFrame
from frame_utils import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    ConfigReset,
)
from page_base import BaseProfilePage

_ = glocale.translation.sgettext


class CitationProfilePage(BaseProfilePage):
    """
    Provides the citation profile page view with information about the citation.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)

    def obj_type(self):
        return 'Citation'

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, citation):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not citation:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "options.citation", self.config,
        )
        self.active_profile = CitationGrampsFrame(grstate, "active", citation)

        source = self.dbstate.db.get_source_from_handle(self.active_profile.obj.source_handle)
        source_frame = SourceGrampsFrame(grstate, "source", source)

        groups = self.config.get("options.citation.layout.groups").split(",")
        obj_groups = {}

        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, citation)})
        if "media" in groups:
            obj_groups.update({"media": get_media_group(grstate, citation)})
        
        people_list = []
        events_list = []
        if "people" in groups or "event" in groups:
            for sub_obj_type, sub_obj_handle in self.dbstate.db.find_backlink_handles(citation.get_handle()):
                if sub_obj_type == "Person":
                    if sub_obj_handle not in people_list:
                        people_list.append(sub_obj_handle)
                    elif sub_obj_type == "Event":
                        if sub_obj_handle not in events_list:
                            events_list.append(sub_obj_handle)

        if people_list:
            people_group = GenericGrampsFrameGroup(grstate, "Person", people_list)
            people = Gtk.Expander(expanded=True, use_markup=True)
            people.set_label("<small><b>{}</b></small>".format(_("Referenced People")))
            people.add(people_group)
            obj_groups.update({"people": people})

        if events_list:
            events_group = GenericGrampsFrameGroup(grstate, "Event", events_list)
            events = Gtk.Expander(expanded=True, use_markup=True)
            events.set_label("<small><b>{}</b></small>".format(_("Referenced Events")))
            events.add(events_group)
            obj_groups.update({"event": events})

        body = self.render_group_view(obj_groups)
        hbox = Gtk.VBox()
        hbox.pack_start(source_frame, True, True, 0)
        hbox.pack_start(self.active_profile, True, True, 0)
        if self.config.get("options.citation.page.pinned-header"):
            header.pack_start(hbox, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(hbox, False, False, 0)
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
            3, "options.citation.page.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Use smaller font for detail attributes"),
            7, "options.citation.page.use-smaller-detail-font",
            tooltip=_("Enabling this option uses a smaller font for all the detailed information than used for the title.")
        )
        configdialog.add_spinner(
            grid, _("Desired border width"),
            8, "options.citation.page.border-width",
            (0, 5),
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            9, "options.citation.page.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Sort tags by name not priority"),
            11, "options.citation.page.sort-tags-by-name",
            tooltip=_("Enabling this option will sort tags by name before displaying them. By default they sort by the priority in which they are organized in the tag organization tool.")
        )
        configdialog.add_checkbox(
            grid, _("Include notes on child objects"),
            12, "options.citation.page.include-child-notes",
            tooltip=_("Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present.")
        )
        configdialog.add_checkbox(
            grid, _("Enable warnings"),
            13, "options.citation.page.enable-warnings",
            tooltip=_("Enabling this will raise a warning dialog asking for confirmation before performing an action that removes or deletes data as a safeguard.")
        )
        configdialog.add_checkbox(
            grid, _("Enable tooltips"),
            14, "options.citation.page.enable-tooltips",
            tooltip=_("TBD TODO. If implemented some tooltips may be added to the view as an aid for new Gramps users which would quickly become annoying so this would turn them off for experienced users.")
        )
        reset = ConfigReset(configdialog, self.config, "options.citation.page", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Page"), grid

    def active_panel(self, configdialog):
        """
        Builds active source options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.citation.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.citation.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.citation.active.tag-width",
            (1, 20)
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "options.citation.active", 16, start_col=1, number=4, obj_type="Source")
        reset = ConfigReset(configdialog, self.config, "options.citation.active", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Source"), grid

    def repositories_panel(self, configdialog):
        """
        Builds repositories options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "options.citation.repository.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "options.citation.repository.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show call number"),
            10, "options.citation.repository.show-call-number",
            tooltip=_("Enabling this option will show the source call number at the repository if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show media type"),
            11, "options.citation.repository.show-media-type",
            tooltip=_("Enabling this option will show the source media type at the repository if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show repository type"),
            12, "options.citation.repository.show-repository-type",
            tooltip=_("Enabling this option will show the repository type if it is available.")
        )
        reset = ConfigReset(configdialog, self.config, "options.citation.repository", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Repositories"), grid

    def people_panel(self, configdialog):
        """
        Builds people options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.citation.people.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.citation.people.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.citation.people.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.citation.people.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.citation.people.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.citation.people.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.citation.people", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.citation.people", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.citation.people", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("People"), grid

    def notes_panel(self, configdialog):
        return self._notes_panel(configdialog, "options.citation")

    def media_panel(self, configdialog):
        return self._media_panel(configdialog, "options.citation")
    
    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.page_panel,
            self.active_panel,
            self.repositories_panel,            
            self.notes_panel,
            self.media_panel,
            self.people_panel,
        ]
