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
from frame_base import GrampsState
from frame_event import EventGrampsFrame
from frame_generic import GenericGrampsFrameGroup
from frame_groups import get_citations_group, get_media_group, get_notes_group
from frame_utils import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    ConfigReset,
)
from page_base import BaseProfilePage

_ = glocale.translation.sgettext


class EventProfilePage(BaseProfilePage):
    """
    Provides the event profile page view with information about the event.
    """

    def __init__(self, dbstate, uistate, config, defaults):
        BaseProfilePage.__init__(self, dbstate, uistate, config, defaults)

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
            "preferences.profile.event", self.config, self.defaults
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

        body = Gtk.HBox(vexpand=False, spacing=3)
        
        citations_box = Gtk.VBox(spacing=3)
        citations = get_citations_group(grstate, event)
        if citations is not None:
            citations_box.pack_start(citations, expand=False, fill=False, padding=0)
            body.pack_start(citations_box, True, True, 0)

        people_list = []
        family_list = []
        for obj_type, obj_handle in self.dbstate.db.find_backlink_handles(event.get_handle()):
            if obj_type == "Person" and obj_handle not in people_list:
                people_list.append(obj_handle)
            elif obj_type == "Family" and obj_handle not in family_list:
                family_list.append(obj_handle)

        if people_list:
            people_group = GenericGrampsFrameGroup(grstate, "Person", people_list)
            people = Gtk.Expander(expanded=True, use_markup=True)
            people.set_label("<small><b>{}</b></small>".format(_("Individual Participants")))
            people.add(people_group)
            people_box = Gtk.VBox(spacing=3)
            people_box.pack_start(people, expand=False, fill=False, padding=0)
            body.pack_start(people_box, True, True, 0)

        if family_list:
            family_group = GenericGrampsFrameGroup(grstate, "Family", family_list)
            family = Gtk.Expander(expanded=True, use_markup=True)
            family.set_label("<small><b>{}</b></small>".format(_("Family Participants")))
            family.add(family_group)
            family_box = Gtk.VBox(spacing=3)
            family_box.pack_start(family, expand=False, fill=False, padding=0)
            body.pack_start(family_box, True, True, 0)

        if self.config.get("preferences.profile.event.layout.show-notes"):
            notes_box = Gtk.VBox(spacing=3)
            notes = get_notes_group(grstate, event)
            if notes is not None:
                notes_box.pack_start(notes, expand=False, fill=False, padding=0)
            body.pack_start(notes_box, True, True, 0)

        if self.config.get("preferences.profile.event.layout.show-media"):
            media_box = Gtk.VBox(spacing=3)
            media = get_media_group(grstate, event)
            if media is not None:
                media_box.pack_start(media, expand=False, fill=False, padding=0)
            body.pack_start(media_box, True, True, 0)

        if self.config.get("preferences.profile.event.layout.pinned-header"):
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
            1, "preferences.profile.event.layout.show-notes",
        )        
        configdialog.add_checkbox(
            grid, _("Show associated media"),
            2, "preferences.profile.event.layout.show-media",
        )        
        configdialog.add_checkbox(
            grid, _("Pin active source header so it does not scroll"),
            3, "preferences.profile.event.layout.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_text(grid, _("Styling Options"), 6, bold=True)
        configdialog.add_checkbox(
            grid, _("Use smaller font for detail attributes"),
            7, "preferences.profile.event.layout.use-smaller-detail-font",
            tooltip=_("Enabling this option uses a smaller font for all the detailed information than used for the title.")
        )
        configdialog.add_spinner(
            grid, _("Desired border width"),
            8, "preferences.profile.event.layout.border-width",
            (0, 5),
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            9, "preferences.profile.event.layout.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Right to left"),
            10, "preferences.profile.event.layout.right-to-left",
            tooltip=_("TBD TODO. If implemented this would modify the frame layout and right justify text fields which might provide a nicer view for those who read right to left like Hebrew, Arabic and Persian.")
        )
        configdialog.add_checkbox(
            grid, _("Sort tags by name not priority"),
            11, "preferences.profile.event.layout.sort-tags-by-name",
            tooltip=_("Enabling this option will sort tags by name before displaying them. By default they sort by the priority in which they are organized in the tag organization tool.")
        )
        configdialog.add_checkbox(
            grid, _("Include notes on child objects"),
            12, "preferences.profile.event.layout.include-child-notes",
            tooltip=_("Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present.")
        )
        configdialog.add_checkbox(
            grid, _("Enable warnings"),
            13, "preferences.profile.event.layout.enable-warnings",
            tooltip=_("Enabling this will raise a warning dialog asking for confirmation before performing an action that removes or deletes data as a safeguard.")
        )
        configdialog.add_checkbox(
            grid, _("Enable tooltips"),
            14, "preferences.profile.event.layout.enable-tooltips",
            tooltip=_("TBD TODO. If implemented some tooltips may be added to the view as an aid for new Gramps users which would quickly become annoying so this would turn them off for experienced users.")
        )
        reset = ConfigReset(configdialog, self.config, "preferences.profile.event.layout", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Layout"), grid

    def active_panel(self, configdialog):
        """
        Builds active event options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.event.active.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.event.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.event.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.event.active.tag-width",
            (1, 20)
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=1, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.event.active", 12, start_col=1, number=4, obj_type="Event")
        reset = ConfigReset(configdialog, self.config, "preferences.profile.event.active", defaults=self.defaults, label=_("Reset Page Defaults"))
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
            1, "preferences.profile.event.people.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "preferences.profile.event.people.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "preferences.profile.event.people.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.event.people.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.event.people.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.event.people.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.event.people", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.event.people", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "preferences.profile.event.people", defaults=self.defaults, label=_("Reset Page Defaults"))
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
            1, "preferences.profile.event.family.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.event.family.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.event.family.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.event.family.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=1, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.event.family", 12, start_col=1, number=4, obj_type="Family")
        reset = ConfigReset(configdialog, self.config, "preferences.profile.event.family", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Family"), grid

    def media_panel(self, configdialog):
        """
        Builds media options section for configuration dialog
        """
        return self._media_panel(configdialog, "preferences.profile.event")

    def notes_panel(self, configdialog):
        """
        Builds notes options section for configuration dialog
        """
        return self._notes_panel(configdialog, "preferences.profile.event")

    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.layout_panel,
            self.active_panel,
            self.people_panel,
            self.family_panel,
            self.notes_panel,
            self.media_panel,
        ]

    def edit_active(self, *obj):
        if self.active_profile:
            self.active_profile.edit_object()

    def add_tag(self, trans, object_handle, tag_handle):
        if self.active_profile:
            self.active_profile.add_tag(trans, object_handle, tag_handle)
