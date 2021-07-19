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
Source Profile Page
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


class SourceProfilePage(BaseProfilePage):
    """
    Provides the source profile page view with information about the source.
    """

    def __init__(self, dbstate, uistate, config, defaults):
        BaseProfilePage.__init__(self, dbstate, uistate, config, defaults)

    def obj_type(self):
        return 'Source'

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, source):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not source:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "preferences.profile.source", self.config, self.defaults
        )
        self.active_profile = SourceGrampsFrame(grstate, "active", source)

        repositories_box = Gtk.VBox(spacing=3)
        repositories = get_repositories_group(grstate, source)
        if repositories is not None:
            repositories_box.pack_start(repositories, expand=False, fill=False, padding=0)

        citations_box = Gtk.VBox(spacing=3)
        citations = get_citations_group(grstate, source, sources=False)
        if citations is not None:
            citations_box.pack_start(citations, expand=False, fill=False, padding=0)

        if self.config.get("preferences.profile.source.layout.show-media"):
            media_box = Gtk.VBox(spacing=3)
            media = get_media_group(grstate, source)
            if media is not None:
                media_box.pack_start(media, expand=False, fill=False, padding=0)

        if self.config.get("preferences.profile.source.layout.show-notes"):
            notes_box = Gtk.VBox(spacing=3)
            notes = get_notes_group(grstate, source)
            if notes is not None:
                notes_box.pack_start(notes, expand=False, fill=False, padding=0)

        people_list = []
        events_list = []
        for obj_type, obj_handle in self.dbstate.db.find_backlink_handles(source.get_handle()):
            if obj_type == "Citation":
                for sub_obj_type, sub_obj_handle in self.dbstate.db.find_backlink_handles(obj_handle):
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
            people_box = Gtk.VBox(spacing=3)
            people_box.pack_start(people, expand=False, fill=False, padding=0)

        if events_list:
            events_group = GenericGrampsFrameGroup(grstate, "Event", events_list)
            events = Gtk.Expander(expanded=True, use_markup=True)
            events.set_label("<small><b>{}</b></small>".format(_("Referenced Events")))
            events.add(events_group)
            events_box = Gtk.VBox(spacing=3)
            events_box.pack_start(events, expand=False, fill=False, padding=0)

        body = Gtk.HBox(vexpand=False, spacing=3)
        if repositories:
            body.pack_start(repositories_box, True, True, 0)
        if citations:
            body.pack_start(citations_box, True, True, 0)
        if self.config.get("preferences.profile.source.layout.show-notes") and notes:
            body.pack_start(notes_box, True, True, 0)
        if self.config.get("preferences.profile.source.layout.show-media") and media:
            body.pack_start(media_box, True, True, 0)
        if people_list:
            body.pack_start(people_box, True, True, 0)
        if events_list:
            body.pack_start(events_box, True, True, 0)

        if self.config.get("preferences.profile.source.layout.pinned-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
        return True

    def layout_panel(self, configdialog):
        """
        Builds layout and styling options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Layout Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid, _("Show associated notes"),
            1, "preferences.profile.source.layout.show-notes",
        )
        configdialog.add_checkbox(
            grid, _("Show associated media"),
            2, "preferences.profile.source.layout.show-media",
        )        
        configdialog.add_checkbox(
            grid, _("Pin active source header so it does not scroll"),
            3, "preferences.profile.source.layout.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_text(grid, _("Styling Options"), 6, bold=True)
        configdialog.add_checkbox(
            grid, _("Use smaller font for detail attributes"),
            7, "preferences.profile.source.layout.use-smaller-detail-font",
            tooltip=_("Enabling this option uses a smaller font for all the detailed information than used for the title.")
        )
        configdialog.add_spinner(
            grid, _("Desired border width"),
            8, "preferences.profile.source.layout.border-width",
            (0, 5),
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            9, "preferences.profile.source.layout.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Right to left"),
            10, "preferences.profile.source.layout.right-to-left",
            tooltip=_("TBD TODO. If implemented this would modify the frame layout and right justify text fields which might provide a nicer view for those who read right to left like Hebrew, Arabic and Persian.")
        )
        configdialog.add_checkbox(
            grid, _("Sort tags by name not priority"),
            11, "preferences.profile.source.layout.sort-tags-by-name",
            tooltip=_("Enabling this option will sort tags by name before displaying them. By default they sort by the priority in which they are organized in the tag organization tool.")
        )
        configdialog.add_checkbox(
            grid, _("Include notes on child objects"),
            12, "preferences.profile.source.layout.include-child-notes",
            tooltip=_("Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present.")
        )
        configdialog.add_checkbox(
            grid, _("Enable warnings"),
            13, "preferences.profile.source.layout.enable-warnings",
            tooltip=_("Enabling this will raise a warning dialog asking for confirmation before performing an action that removes or deletes data as a safeguard.")
        )
        configdialog.add_checkbox(
            grid, _("Enable tooltips"),
            14, "preferences.profile.source.layout.enable-tooltips",
            tooltip=_("TBD TODO. If implemented some tooltips may be added to the view as an aid for new Gramps users which would quickly become annoying so this would turn them off for experienced users.")
        )
        reset = ConfigReset(configdialog, self.config, "preferences.profile.source.layout", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Layout"), grid

    def active_panel(self, configdialog):
        """
        Builds active source options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.source.active.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.source.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.source.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.source.active.tag-width",
            (1, 20)
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.source.active", 16, start_col=1, number=4, obj_type="Source")
        reset = ConfigReset(configdialog, self.config, "preferences.profile.source.active", defaults=self.defaults, label=_("Reset Page Defaults"))
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
            1, "preferences.profile.source.repository.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "preferences.profile.source.repository.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show call number"),
            10, "preferences.profile.source.repository.show-call-number",
            tooltip=_("Enabling this option will show the source call number at the repository if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show media type"),
            11, "preferences.profile.source.repository.show-media-type",
            tooltip=_("Enabling this option will show the source media type at the repository if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show repository type"),
            12, "preferences.profile.source.repository.show-repository-type",
            tooltip=_("Enabling this option will show the repository type if it is available.")
        )
        reset = ConfigReset(configdialog, self.config, "preferences.profile.source.repository", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Repositories"), grid

    def citations_panel(self, configdialog):
        """
        Builds citations options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "preferences.profile.source.citation.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "preferences.profile.source.citation.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.source.citation.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Sort citations by date"),
            4, "preferences.profile.source.citation.sort-by-date",
            tooltip=_("Enabling this option will sort the citations by date.")
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show date"),
            10, "preferences.profile.source.citation.show-date",
            tooltip=_("Enabling this option will show the citation date if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show publisher"),
            11, "preferences.profile.source.citation.show-publisher",
            tooltip=_("Enabling this option will show the publisher information if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference type"),
            12, "preferences.profile.source.citation.show-reference-type",
            tooltip=_("Enabling this option will display what type of citation it is. Direct is one related to the person or a family they formed, indirect would be related to some nested attribute like a name or person association.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference description"),
            13, "preferences.profile.source.citation.show-reference-description",
            tooltip=_("Enabling this option will display a description of the type of data the citation supports. For direct citations this would be person or family, indirect ones could be primary name, an attribute, association, address, and so forth.")
        )
        configdialog.add_checkbox(
            grid, _("Show confidence rating"),
            14, "preferences.profile.source.citation.show-confidence",
            tooltip=_("Enabling this option will display the user selected confidence level for the citation.")
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.source.citation", 16, start_col=1, number=4, obj_type="Citation")
        reset = ConfigReset(configdialog, self.config, "preferences.profile.source.citation", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Citations"), grid

    def people_panel(self, configdialog):
        """
        Builds people options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.source.people.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "preferences.profile.source.people.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "preferences.profile.source.people.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.source.people.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.source.people.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.source.people.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.source.people", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.source.people", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "preferences.profile.source.people", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("People"), grid

    def notes_panel(self, configdialog):
        return self._notes_panel(configdialog, "preferences.profile.source")

    def media_panel(self, configdialog):
        return self._media_panel(configdialog, "preferences.profile.source")
    
    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.layout_panel,
            self.active_panel,
            self.repositories_panel,            
            self.citations_panel,
            self.notes_panel,
            self.media_panel,
            self.people_panel,
        ]

    def edit_active(self, *obj):
        if self.active_profile:
            self.active_profile.edit_object()

    def add_tag(self, trans, object_handle, tag_handle):
        if self.active_profile:
            self.active_profile.add_tag(trans, object_handle, tag_handle)
