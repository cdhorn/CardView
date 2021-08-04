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
Person Profile Page
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
    _LEFT_BUTTON,
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TIMELINE_COLOR_MODES,
)    
from ..frames.frame_person import PersonGrampsFrame
from ..frames.frame_utils import (
    button_activated,
    ConfigReset,
    LayoutEditorButton
)
from ..groups.group_utils import (
    get_addresses_group,
    get_associations_group,
    get_citations_group,
    get_media_group,
    get_names_group,
    get_notes_group,
    get_parents_group,
    get_spouses_group,
    get_timeline_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class PersonProfilePage(BaseProfilePage):
    """
    Provides the person profile page view with information about the person.
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
        return 'Person'

    def page_type(self):
        return 'Person'

    def define_actions(self, view):
        self.order_action = ActionGroup(name='ChangeOrder')
        self.order_action.add_actions([
            ('ChangeOrder', self.reorder)])

        self.family_action = ActionGroup(name='Family')
        self.family_action.add_actions([
            ('AddSpouse', self.add_spouse),
            ('AddParents', self.add_parents),
            ('ShareFamily', self.select_parents)])

        view._add_action_group(self.order_action)
        view._add_action_group(self.family_action)

    def enable_actions(self, uimanager, person):
        uimanager.set_actions_visible(self.family_action, True)
        uimanager.set_actions_visible(self.order_action, True)

    def disable_actions(self, uimanager):
        uimanager.set_actions_visible(self.family_action, False)
        uimanager.set_actions_visible(self.order_action, False)

    def render_page(self, header, vbox, person, secondary=None):
        list(map(header.remove, header.get_children()))        
        list(map(vbox.remove, vbox.get_children()))
        if not person:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "options.person", self.config
        )
        self.active_profile = PersonGrampsFrame(grstate, "active", person)

        groups = self.config.get("options.person.layout.groups").split(",")
        obj_groups = {}

        if "parent" in groups:
            obj_groups.update({"parent": get_parents_group(grstate, person)})
        if "spouse" in groups:
            obj_groups.update({"spouse": get_spouses_group(grstate, person)})
        if "name" in groups:
            obj_groups.update({"name": get_names_group(grstate, person)})
        if "association" in groups:
            obj_groups.update({"association": get_associations_group(grstate, person)})
        if "timeline" in groups:
            obj_groups.update({"timeline": get_timeline_group(grstate, person)})
        if "citation" in groups:
            obj_groups.update({"citation": get_citations_group(grstate, person)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, person)})
        if "media" in groups:
            obj_groups.update({"media": get_media_group(grstate, person)})
        if "address" in groups:
            obj_groups.update({"address": get_addresses_group(grstate, person)})
        body = self.render_group_view(obj_groups)

        if self.config.get("options.person.page.pinned-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        self.child = body
        vbox.pack_start(self.child, True, True, 0)
        vbox.show_all()

        family_handle_list = person.get_parent_family_handle_list()
        self.reorder_sensitive = len(family_handle_list) > 1
        family_handle_list = person.get_family_handle_list()
        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list) > 1
        return True

    def reorder_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *obj):
        if self.active_profile:
            try:
                Reorder(self.dbstate, self.uistate, [], self.active_profile.obj.get_handle())
            except WindowActiveError:
                pass

    def page_panel(self, configdialog):
        """
        Builds page and styling options section for the configuration dialog
        """
        grid = self.create_grid()
        self._config_global_options(configdialog, grid, 0)
        configdialog.add_text(grid, _("Page Options"), 10, bold=True)
        configdialog.add_checkbox(
            grid, _("Pin active person header so it does not scroll"),
            11, "options.person.page.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            12, "options.person.page.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Include notes on child objects"),
            13, "options.person.page.include-child-notes",
            tooltip=_("Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present.")
        )
        editor = LayoutEditorButton(self.uistate, self.config, "Person")
        grid.attach(editor, 1, 19, 1, 1)        
        reset = ConfigReset(configdialog, self.config, "options.person.page", label=_("Reset Page Defaults"))
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
            1, "options.person.active.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.person.active.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.person.active.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.person.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.person.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.person.active.tag-width",
            (1, 20)
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 8, bold=True)
        self._config_facts_fields(configdialog, grid, "options.person.active", 9)
        configdialog.add_text(grid, _("Extra Fact Display Fields"), 8, start=3, bold=True)
        self._config_facts_fields(configdialog, grid, "options.person.active", 9, start_col=3, extra=True)
        configdialog.add_text(grid, _("Metadata Display Fields"), 8, start=5, bold=True)
        self._config_metadata_attributes(grid, "options.person.active", 9, start_col=5)
        reset = ConfigReset(configdialog, self.config, "options.person.active", label=_("Reset Page Defaults"))
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
            1, "options.person.parent.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.person.parent.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.person.parent.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Expand children by default"),
            2, "options.person.parent.expand-children", start=3,
            tooltip=_("Enabling this option will automatically expand the list of children when the page is rendered.")
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.person.parent.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Matrilineal mode (inverts couple)"),
            3, "options.person.parent.show-matrilineal", start=3,
            tooltip=_("Enabling this option will switch the placement of the male and female roles in the couple relationship.")
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.person.parent.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.person.parent.tag-width",
            (1, 20),
        )
        configdialog.add_checkbox(
            grid, _("Show divorce or divorce equivalent"),
            6, "options.person.parent.show-divorce"
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.person.parent", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.person.parent", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.person.parent", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Parents"), grid

    def spouses_panel(self, configdialog):
        """
        Builds spouses options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.person.spouse.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.person.spouse.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.person.spouse.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Expand children by default"),
            2, "options.person.spouse.expand-children", start=3,
            tooltip=_("Enabling this option will automatically expand the list of children when the page is rendered.")
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.person.spouse.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.person.spouse.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.person.spouse.tag-width",
            (1, 20),
        )
        configdialog.add_checkbox(
            grid, _("Show spouse only"),
            6, "options.person.spouse.show-spouse-only",
        )
        configdialog.add_checkbox(
            grid, _("Show divorce or divorce equivalent"),
            6, "options.person.spouse.show-divorce", start=3
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 13, bold=True)
        self._config_facts_fields(configdialog, grid, "options.person.spouse", 14)
        configdialog.add_text(grid, _("Metadata Display Fields"), 13, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.person.spouse", 14, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.person.spouse", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Spouses"), grid

    def children_panel(self, configdialog):
        """
        Builds children options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.person.child.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.person.child.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.person.child.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Number children"),
            2, "options.person.child.number-children", start=3
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.person.child.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.person.child.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.person.child.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.person.child", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.person.child", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.person.child", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Children"), grid

    def siblings_panel(self, configdialog):
        """
        Builds siblings options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.person.sibling.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.person.sibling.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.person.sibling.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Number children"),
            2, "options.person.sibling.number-children", start=3
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.person.sibling.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.person.sibling.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.person.sibling.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.person.sibling", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.person.sibling", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.person.sibling", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Siblings"), grid

    def associations_panel(self, configdialog):
        """
        Builds associations options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "options.person.association.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "options.person.association.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "options.person.association.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.person.association.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "options.person.association.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "options.person.association.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "options.person.association", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "options.person.association", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "options.person.association", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Associations"), grid
    
    def timeline_panel(self, configdialog):
        """
        Builds active person timeline options section for the configuration dialog
        """
        grid1 = self.create_grid()
        configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid1, _("Timeline color scheme"),
            1, "options.person.timeline.color-scheme",
            TIMELINE_COLOR_MODES,
        )
        configdialog.add_combo(
            grid1, _("Tag display mode"),
            2, "options.person.timeline.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid1, _("Maximum tags per line"),
            3, "options.person.timeline.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid1, _("Image display mode"),
            4, "options.person.timeline.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid1, _("Show year and age"),
            5, "options.person.timeline.show-age",
            tooltip=_("Enabling this option will show the year of the event and the age of the active person at that time if it can be calculated.")
        )
        configdialog.add_text(grid1, _("Display Attributes"), 6, bold=True)
        configdialog.add_checkbox(
            grid1, _("Show role always not just secondary events"),
            7, "options.person.timeline.show-role-always",
            tooltip=_("Enabling this option will always show the role of the active person in the event. This is normally implicit if they had none or they were the primary participant. Note their role is always displayed for secondary events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show description"),
            8, "options.person.timeline.show-description",
            tooltip=_("Enabling this option will show the event description if one is available.")
        )
        configdialog.add_checkbox(
            grid1, _("Show registered participants if more than one person"),
            9, "options.person.timeline.show-participants",
            tooltip=_("Enabling this option will show the other participants in shared events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show source count"),
            10, "options.person.timeline.show-source-count",
            tooltip=_("Enabling this option will include a count of the number of unique sources cited from in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show citation count"),
            11, "options.person.timeline.show-citation-count",
            tooltip=_("Enabling this option will include a count of the number of citations in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show best confidence rating"),
            12, "options.person.timeline.show-best-confidence",
            tooltip=_("Enabling this option will show the highest user defined confidence rating found among all the citations in support of the information about the event.")
        )
        configdialog.add_text(grid1, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid1, "options.person.timeline", 16, start_col=1, number=4, obj_type="Event")
        reset = ConfigReset(configdialog, self.config, "options.person.timeline", label=_("Reset Page Defaults"))
        grid1.attach(reset, 1, 25, 1, 1)
        grid2 = self.create_grid()
        configdialog.add_text(grid2, _("Category Filters"), 0, bold=True)
        configdialog.add_checkbox(
            grid2, _("Show vital"),
            1, "options.person.timeline.show-class-vital",
            tooltip=_("Enabling this option will show all vital events for the person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others.")
        )
        configdialog.add_checkbox(
            grid2, _("Show family"),
            2, "options.person.timeline.show-class-family",
            tooltip=_("Enabling this option will show all family related events for the active person on the timeline. The list of family events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show religious"),
            3, "options.person.timeline.show-class-religious",
            tooltip=_("Enabling this option will show all religious events for the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show vocational"),
            4, "options.person.timeline.show-class-vocational",
            tooltip=_("Enabling this option will show all vocational events for the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show academic"),
            5, "options.person.timeline.show-class-academic",
            tooltip=_("Enabling this option will show all academic events for the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show travel"),
            6, "options.person.timeline.show-class-travel",
            tooltip=_("Enabling this option will show all travel events for the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show legal"),
            7, "options.person.timeline.show-class-legal",
            tooltip=_("Enabling this option will show all legal events for the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show residence"),
            8, "options.person.timeline.show-class-residence",
            tooltip=_("Enabling this option will show all residence events for the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show other"),
            9, "options.person.timeline.show-class-other",
            tooltip=_("Enabling this option will show all other events for the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show custom"),
            10, "options.person.timeline.show-class-custom",
            tooltip=_("Enabling this option will show all user defined custom events for the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor.")
        )
        grid3 = self.create_grid()
        configdialog.add_text(grid3, _("Relationship Filters"), 0, bold=True)
        configdialog.add_spinner(
            grid3, _("Generations of ancestors to examine"),
            1, "options.person.timeline.generations-ancestors",
            (1, 3),
        )
        configdialog.add_spinner(
            grid3, _("Generations of offspring to examine"),
            2, "options.person.timeline.generations-offspring",
            (1, 3),
        )
        configdialog.add_checkbox(
            grid3, _("Include events for father and grandfathers"),
            3, "options.person.timeline.show-family-father",
            tooltip=_("Enabling this option will include events for fathers, stepfathers, and grandfathers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for mother and grandmothers"),
            4, "options.person.timeline.show-family-mother",
            tooltip=_("Enabling this option will include events for mothers, stepmothers, and grandmothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for brothers and stepbrothers"),
            5, "options.person.timeline.show-family-brother",
            tooltip=_("Enabling this option will include events for brothers and stepbrothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for sisters and stepsisters"),
            6, "options.person.timeline.show-family-sister",
            tooltip=_("Enabling this option will include events for sisters and stepsisters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for wives"),
            7, "options.person.timeline.show-family-wife",
            tooltip=_("Enabling this option will include events for the wives of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for husbands"),
            8, "options.person.timeline.show-family-husband",
            tooltip=_("Enabling this option will include events for the husbands of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for sons and grandsons"),
            9, "options.person.timeline.show-family-son",
            tooltip=_("Enabling this option will include events for the sons and grandsons of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for daughters and granddaughters"),
            10, "options.person.timeline.show-family-daughter",
            tooltip=_("Enabling this option will include events for the daughters and granddaughters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        grid4 = self.create_grid()
        configdialog.add_text(grid4, _("Relationship Category Filters"), 0, bold=True)
        configdialog.add_checkbox(
            grid4, _("Show vital"),
            1, "options.person.timeline.show-family-class-vital",
            tooltip=_("Enabling this option will show all vital events for the eligible relations of the active person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others.")
        )
        configdialog.add_checkbox(
            grid4, _("Show family"),
            2, "options.person.timeline.show-family-class-family",
            tooltip=_("Enabling this option will show all family related events for the eligible relations of the active person on the timeline. The list of family events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show religious"),
            3, "options.person.timeline.show-family-class-religious",
            tooltip=_("Enabling this option will show all religious related events for the eligible relations of the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show vocational"),
            4, "options.person.timeline.show-family-class-vocational",
            tooltip=_("Enabling this option will show all vocational related events for the eligible relations of the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show academic"),
            5, "options.person.timeline.show-family-class-academic",
            tooltip=_("Enabling this option will show all academic related events for the eligible relations of the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show travel"),
            6, "options.person.timeline.show-family-class-travel",
            tooltip=_("Enabling this option will show all travel related events for the eligible relations of the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show legal"),
            7, "options.person.timeline.show-family-class-legal",
            tooltip=_("Enabling this option will show all legal related events for the eligible relations of the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show residence"),
            8, "options.person.timeline.show-family-class-residence",
            tooltip=_("Enabling this option will show all residence related events for the eligible relations of the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show other"),
            9, "options.person.timeline.show-family-class-other",
            tooltip=_("Enabling this option will show all other events for the eligible relations of the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show custom"),
            10, "options.person.timeline.show-family-class-custom",
            tooltip=_("Enabling this option will show all user defined custom events for the eligible relations of the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor.")
        )
        grid = Gtk.Grid()
        grid.attach(grid1, 0, 0, 1, 1)
        grid.attach(grid2, 1, 0, 1, 1)
        grid.attach(grid3, 2, 0, 1, 1)
        grid.attach(grid4, 3, 0, 1, 1)
        return _("Timeline"), grid

    def citations_panel(self, configdialog):
        """
        Builds citations options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "options.person.citation.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "options.person.citation.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "options.person.citation.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Sort citations by date"),
            4, "options.person.citation.sort-by-date",
            tooltip=_("Enabling this option will sort the citations by date.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations about the person"),
            5, "options.person.citation.include-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes like names and person associations in addition to the ones directly on the person themselves.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a child"),
            6, "options.person.citation.include-parent-family",
            tooltip=_("Enabling this option will include citations related to the membership of the person as a child in other families.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a head of household"),
            7, "options.person.citation.include-family",
            tooltip=_("Enabling this option will include citations on the families this person formed with other partners.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations related to the persons family membership as a head of household"),
            8, "options.person.citation.include-family-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes about the families this person formed with other partners.")
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show date"),
            10, "options.person.citation.show-date",
            tooltip=_("Enabling this option will show the citation date if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show publisher"),
            11, "options.person.citation.show-publisher",
            tooltip=_("Enabling this option will show the publisher information if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference type"),
            12, "options.person.citation.show-reference-type",
            tooltip=_("Enabling this option will display what type of citation it is. Direct is one related to the person or a family they formed, indirect would be related to some nested attribute like a name or person association.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference description"),
            13, "options.person.citation.show-reference-description",
            tooltip=_("Enabling this option will display a description of the type of data the citation supports. For direct citations this would be person or family, indirect ones could be primary name, an attribute, association, address, and so forth.")
        )
        configdialog.add_checkbox(
            grid, _("Show confidence rating"),
            14, "options.person.citation.show-confidence",
            tooltip=_("Enabling this option will display the user selected confidence level for the citation.")
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "options.person.citation", 16, start_col=1, number=4, obj_type="Citation")
        reset = ConfigReset(configdialog, self.config, "options.person.citation", label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Citations"), grid

    def media_panel(self, configdialog):
        """
        Builds media options section for configuration dialog
        """
        return self._media_panel(configdialog, "options.person")

    def notes_panel(self, configdialog):
        """
        Builds notes options section for configuration dialog
        """
        return self._notes_panel(configdialog, "options.person")

    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.page_panel,
            self.color_panel,
            self.active_panel,
            self.parents_panel,
            self.siblings_panel,
            self.spouses_panel,
            self.children_panel,
            self.associations_panel,
            self.timeline_panel,
            self.citations_panel,
            self.notes_panel,
            self.media_panel,
        ]

    def add_spouse(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_spouse()

    def select_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_existing_parents()

    def add_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_parents()
