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
Family Profile Page
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
from gramps.gen.errors import WindowActiveError
from gramps.gui.uimanager import ActionGroup
from gramps.gui.widgets.reorderfam import Reorder


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames.frame_classes import GrampsState
from ..frames.frame_const import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TIMELINE_COLOR_MODES,
)    
from ..frames.frame_person import PersonGrampsFrame
from ..frames.frame_couple import CoupleGrampsFrame
from ..frames.frame_utils import (
    ConfigReset,
    LayoutEditorButton
)
from ..groups.group_utils import (
    get_children_group,
    get_citations_group,
    get_media_group,
    get_notes_group,
    get_timeline_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class FamilyProfilePage(BaseProfilePage):
    """
    Provides the family profile page view with information about the family.
    """

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)
        self.order_action = None
        self.family_action = None
        self.reorder_sensitive = None
        self.child = None
        self.colors = None
        self.active_profile = None

    def obj_type(self):
        return 'Family'

    def page_type(self):
        return 'Family'

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def _get_primary_parents(self, grstate, person, groups):
        if person:
            primary_handle = person.get_main_parents_family_handle()
            if primary_handle:
                family = self.dbstate.db.get_family_from_handle(primary_handle)
                return CoupleGrampsFrame(
                    grstate,
                    "parent",
                    family,
                    relation=person,
                )
        return None
            
    def render_page(self, header, vbox, family, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not family:
            return

        groups = {
            "partner1": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "partner2": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        p1groups = {
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        p2groups = {
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "options.family", self.config, 
        )
        self.active_profile = CoupleGrampsFrame(
            grstate,
            "active",
            family,
            groups=groups,
            vertical=False
        )

        pbox = Gtk.HBox(vexpand=False, hexpand=True, spacing=3, margin_bottom=3)
        p1parents = self._get_primary_parents(grstate, self.active_profile.parent1, p1groups)
        p2parents = self._get_primary_parents(grstate, self.active_profile.parent2, p2groups)
        if p1parents:
            groups['partner1'].add_widget(p1parents)
            pbox.pack_start(p1parents, expand=True, fill=True, padding=0)
        if p2parents:
            groups['partner2'].add_widget(p2parents)
            pbox.pack_start(p2parents, expand=True, fill=True, padding=0)

        vbox.pack_start(pbox, expand=True, fill=True, padding=0)
        vbox.pack_start(self.active_profile, expand=True, fill=True, padding=0)

        groups = self.config.get("options.family.layout.groups").split(",")
        obj_groups = {}

        if "child" in groups:
            obj_groups.update({"child": get_children_group(grstate, family)})
        if "timeline" in groups:
            obj_groups.update({"timeline": get_timeline_group(grstate, family)})
        if "citation" in groups:
            obj_groups.update({"citation": get_citations_group(grstate, family)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, family)})
        if "media" in groups:
            obj_groups.update({"media": get_media_group(grstate, family)})
        body = self.render_group_view(obj_groups)

        vbox.pack_start(body, True, True, 0)
        vbox.show_all()
        return True

    def page_panel(self, configdialog):
        """
        Builds styling and page options section for the configuration dialog
        """
        grid = self.create_grid()
        self._config_global_options(configdialog, grid, 0)
        configdialog.add_text(grid, _("Page Options"), 10, bold=True)
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            11, "options.family.page.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Include notes on child objects"),
            12, "options.family.page.include-child-notes",
            tooltip=_("Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present.")
        )
        editor = LayoutEditorButton(self.uistate, self.config, "Family")
        grid.attach(editor, 1, 19, 1, 1)
        reset = ConfigReset(configdialog, self.config, "options.family.page", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Page"), grid

    def active_panel(self, configdialog):
        """
        Builds active person options section for the configuration dialog
        """
        grid = self.create_grid()        
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.family.active.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.family.active.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.family.active.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.family.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.family.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.family.active.tag-width",
            (1, 20)
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 8, bold=True)
        self._config_facts_fields(configdialog, grid, "options.family.active", 9)
        configdialog.add_text(grid, _("Metadata Display Fields"), 8, start=5, bold=True)
        self._config_metadata_attributes(grid, "options.family.active", 9, start_col=5)
        reset = ConfigReset(configdialog, self.config, "options.family.active", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Person"), grid

    def parents_panel(self, configdialog):
        """
        Builds parents options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.family.parent.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.family.parent.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.family.parent.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Expand children by default"),
            2, "options.family.parent.expand-children", start=3,
            tooltip=_("Enabling this option will automatically expand the list of children when the page is rendered.")
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.family.parent.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Matrilineal mode (inverts couple)"),
            3, "options.family.parent.show-matrilineal", start=3,
            tooltip=_("Enabling this option will switch the placement of the male and female roles in the couple relationship.")
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.family.parent.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.family.parent.tag-width",
            (1, 20),
        )
        configdialog.add_checkbox(
            grid, _("Show divorce or divorce equivalent"),
            6, "options.family.parent.show-divorce"
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.family.parent", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.family.parent", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.family.parent", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Parents"), grid

    def children_panel(self, configdialog):
        """
        Builds children options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.family.child.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.family.child.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.family.child.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Number children"),
            2, "options.family.child.number-children", start=3
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.family.child.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.family.child.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.family.child.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.family.child", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.family.child", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.family.child", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Children"), grid

    def timeline_panel(self, configdialog):
        """
        Builds active family timeline options section for the configuration dialog
        """
        grid1 = self.create_grid()
        configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid1, _("Timeline color scheme"),
            1, "options.family.timeline.color-scheme",
            TIMELINE_COLOR_MODES,
        )
        configdialog.add_combo(
            grid1, _("Tag display mode"),
            2, "options.family.timeline.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid1, _("Maximum tags per line"),
            3, "options.family.timeline.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid1, _("Image display mode"),
            4, "options.family.timeline.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid1, _("Show year and age"),
            5, "options.family.timeline.show-age",
            tooltip=_("Enabling this option will show the year of the event and the age of the active person at that time if it can be calculated.")
        )
        configdialog.add_text(grid1, _("Display Attributes"), 6, bold=True)
        configdialog.add_checkbox(
            grid1, _("Show role always not just secondary events"),
            7, "options.family.timeline.show-role-always",
            tooltip=_("Enabling this option will always show the role of the active person in the event. This is normally implicit if they had none or they were the primary participant. Note their role is always displayed for secondary events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show description"),
            8, "options.family.timeline.show-description",
            tooltip=_("Enabling this option will show the event description if one is available.")
        )
        configdialog.add_checkbox(
            grid1, _("Show registered participants if more than one person"),
            9, "options.family.timeline.show-participants",
            tooltip=_("Enabling this option will show the other participants in shared events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show source count"),
            10, "options.family.timeline.show-source-count",
            tooltip=_("Enabling this option will include a count of the number of unique sources cited from in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show citation count"),
            11, "options.family.timeline.show-citation-count",
            tooltip=_("Enabling this option will include a count of the number of citations in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show best confidence rating"),
            12, "options.family.timeline.show-best-confidence",
            tooltip=_("Enabling this option will show the highest user defined confidence rating found among all the citations in support of the information about the event.")
        )
        configdialog.add_text(grid1, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid1, "options.family.timeline", 16, start_col=1, number=4, obj_type="Event")
        reset = ConfigReset(configdialog, self.config, "options.family.timeline", label=_("Reset Page Defaults"))
        grid1.attach(reset, 1, 25, 1, 1)
        grid2 = self.create_grid()
        configdialog.add_text(grid2, _("Category Filters"), 0, bold=True)
        configdialog.add_checkbox(
            grid2, _("Show vital"),
            1, "options.family.timeline.show-class-vital",
            tooltip=_("Enabling this option will show all vital events for the person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others.")
        )
        configdialog.add_checkbox(
            grid2, _("Show family"),
            2, "options.family.timeline.show-class-family",
            tooltip=_("Enabling this option will show all family related events for the active person on the timeline. The list of family events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show religious"),
            3, "options.family.timeline.show-class-religious",
            tooltip=_("Enabling this option will show all religious events for the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show vocational"),
            4, "options.family.timeline.show-class-vocational",
            tooltip=_("Enabling this option will show all vocational events for the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show academic"),
            5, "options.family.timeline.show-class-academic",
            tooltip=_("Enabling this option will show all academic events for the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show travel"),
            6, "options.family.timeline.show-class-travel",
            tooltip=_("Enabling this option will show all travel events for the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show legal"),
            7, "options.family.timeline.show-class-legal",
            tooltip=_("Enabling this option will show all legal events for the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show residence"),
            8, "options.family.timeline.show-class-residence",
            tooltip=_("Enabling this option will show all residence events for the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show other"),
            9, "options.family.timeline.show-class-other",
            tooltip=_("Enabling this option will show all other events for the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show custom"),
            10, "options.family.timeline.show-class-custom",
            tooltip=_("Enabling this option will show all user defined custom events for the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor.")
        )
        grid = Gtk.Grid()
        grid.attach(grid1, 0, 0, 1, 1)
        grid.attach(grid2, 1, 0, 1, 1)
        return _("Timeline"), grid

    def citations_panel(self, configdialog):
        """
        Builds citations options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "options.family.citation.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "options.family.citation.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.family.citation.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Sort citations by date"),
            4, "options.family.citation.sort-by-date",
            tooltip=_("Enabling this option will sort the citations by date.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations about the person"),
            5, "options.family.citation.include-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes like names and person associations in addition to the ones directly on the person themselves.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a child"),
            6, "options.family.citation.include-parent-family",
            tooltip=_("Enabling this option will include citations related to the membership of the person as a child in other families.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a head of household"),
            7, "options.family.citation.include-family",
            tooltip=_("Enabling this option will include citations on the families this person formed with other partners.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations related to the persons family membership as a head of household"),
            8, "options.family.citation.include-family-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes about the families this person formed with other partners.")
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show date"),
            10, "options.family.citation.show-date",
            tooltip=_("Enabling this option will show the citation date if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show publisher"),
            11, "options.family.citation.show-publisher",
            tooltip=_("Enabling this option will show the publisher information if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference type"),
            12, "options.family.citation.show-reference-type",
            tooltip=_("Enabling this option will display what type of citation it is. Direct is one related to the person or a family they formed, indirect would be related to some nested attribute like a name or person association.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference description"),
            13, "options.family.citation.show-reference-description",
            tooltip=_("Enabling this option will display a description of the type of data the citation supports. For direct citations this would be person or family, indirect ones could be primary name, an attribute, association, address, and so forth.")
        )
        configdialog.add_checkbox(
            grid, _("Show confidence rating"),
            14, "options.family.citation.show-confidence",
            tooltip=_("Enabling this option will display the user selected confidence level for the citation.")
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "options.family.citation", 16, start_col=1, number=4, obj_type="Citation")
        reset = ConfigReset(configdialog, self.config, "options.family.citation", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Citations"), grid

    def media_panel(self, configdialog):
        """
        Builds media options section for configuration dialog
        """
        return self._media_panel(configdialog, "options.family")

    def notes_panel(self, configdialog):
        """
        Builds notes options section for configuration dialog
        """
        return self._notes_panel(configdialog, "options.family")

    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.page_panel,
            self.color_panel,
            self.active_panel,
            self.parents_panel,
            self.children_panel,
            self.timeline_panel,
            self.citations_panel,
            self.notes_panel,
            self.media_panel,
        ]
