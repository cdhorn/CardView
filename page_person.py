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
from frame_base import GrampsState, button_activated
from frame_groups import (
    get_citation_group,
    get_media_group,
    get_parents_group,
    get_spouses_group,
    get_timeline_group,
)
from frame_person import PersonGrampsFrame
from frame_utils import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
    TIMELINE_COLOR_MODES,
    AttributeSelector,
    ConfigReset,
    FrameFieldSelector
)
from page_base import BaseProfilePage

_ = glocale.translation.sgettext
_LEFT_BUTTON = 1


class PersonProfilePage(BaseProfilePage):
    """
    Provides the person profile page view with information about the person.
    """

    def __init__(self, dbstate, uistate, config, defaults):
        BaseProfilePage.__init__(self, dbstate, uistate, config, defaults)
        self.order_action = None
        self.family_action = None
        self.reorder_sensitive = None
        self.child = None
        self.colors = None
        self.active_profile = None

    def obj_type(self):
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

    def render_page(self, header, vbox, person):
        list(map(header.remove, header.get_children()))        
        list(map(vbox.remove, vbox.get_children()))
        if not person:
            return

        grstate = GrampsState(
            self.dbstate, self.uistate, self.callback_router,
            "preferences.profile.person", self.config, self.defaults
        )
        self.active_profile = PersonGrampsFrame(grstate, "active", person)

        body = Gtk.HBox(expand=True, spacing=3)
        parents_box = Gtk.VBox(spacing=3)
        parents = get_parents_group(grstate, person)
        if parents is not None:
            parents_box.pack_start(parents, expand=False, fill=False, padding=0)

        spouses_box = Gtk.VBox(spacing=3)
        spouses = get_spouses_group(grstate, person)
        if spouses is not None:
            spouses_box.pack_start(spouses, expand=False, fill=False, padding=0)

        if self.config.get("preferences.profile.person.layout.show-timeline"):
            timeline_box = Gtk.VBox(spacing=3)
            timeline = get_timeline_group(grstate, person)
            if timeline is not None:
                timeline_box.pack_start(timeline, expand=False, fill=False, padding=0)

        if self.config.get("preferences.profile.person.layout.show-citations"):
            citations_box = Gtk.VBox(spacing=3)
            citations = get_citation_group(grstate, person)
            if citations is not None:
                citations_box.pack_start(citations, expand=False, fill=False, padding=0)

        if self.config.get("preferences.profile.person.layout.show-media"):
            media_box = Gtk.VBox(spacing=3)
            media = get_media_group(grstate, person)
            if media is not None:
                media_box.pack_start(media, expand=False, fill=False, padding=0)

        if self.config.get("preferences.profile.person.layout.families-stacked"):
            families_box = Gtk.VBox(spacing=3)
            families_box.pack_start(parents_box, expand=False, fill=False, padding=0)
            families_box.pack_start(spouses_box, expand=False, fill=False, padding=0)
            if self.config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(families_box, expand=True, fill=True, padding=0)
            if self.config.get("preferences.profile.person.layout.show-timeline"):
                body.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self.config.get("preferences.profile.person.layout.show-citations"):
                body.pack_start(citations_box, expand=True, fill=True, padding=0)
            if self.config.get("preferences.profile.person.layout.show-media"):
                body.pack_start(media_box, expand=True, fill=True, padding=0)
            if not self.config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(families_box, expand=True, fill=True, padding=0)
        else:
            if self.config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(spouses_box, expand=True, fill=True, padding=0)
            else:
                body.pack_start(parents_box, expand=True, fill=True, padding=0)
            if self.config.get("preferences.profile.person.layout.show-timeline"):
                body.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self.config.get("preferences.profile.person.layout.show-citations"):
                body.pack_start(citations_box, expand=True, fill=True, padding=0)
            if self.config.get("preferences.profile.person.layout.show-media"):
                body.pack_start(media_box, expand=True, fill=True, padding=0)
            if self.config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(parents_box, expand=True, fill=True, padding=0)
            else:
                body.pack_start(spouses_box, expand=True, fill=True, padding=0)

        if self.config.get("preferences.profile.person.layout.pinned-header"):
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
        if self.get_active():
            try:
                Reorder(self.dbstate, self.uistate, [], self.get_active())
            except WindowActiveError:
                pass

    def layout_panel(self, configdialog):
        """
        Builds layout and styling options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Layout Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid, _("Pin active person header so it does not scroll"),
            1, "preferences.profile.person.layout.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Place spouses & children on left side"),
            2, "preferences.profile.person.layout.spouses-left",
        )
        configdialog.add_checkbox(
            grid, _("Stack parents & spouses in a single column"),
            3, "preferences.profile.person.layout.families-stacked",
        )
        configdialog.add_checkbox(
            grid, _("Show event timeline"),
            4, "preferences.profile.person.layout.show-timeline",
        )
        configdialog.add_checkbox(
            grid, _("Show associated citations"),
            5, "preferences.profile.person.layout.show-citations",
        )
        configdialog.add_text(grid, _("Styling Options"), 6, bold=True)
        configdialog.add_checkbox(
            grid, _("Use smaller font for detail attributes"),
            7, "preferences.profile.person.layout.use-smaller-detail-font",
            tooltip=_("Enabling this option uses a smaller font for all the detailed information than used for the title.")
        )
        configdialog.add_spinner(
            grid, _("Desired border width"),
            8, "preferences.profile.person.layout.border-width",
            (0, 5),
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            9, "preferences.profile.person.layout.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Right to left"),
            10, "preferences.profile.person.layout.right-to-left",
            tooltip=_("TBD TODO. If implemented this would modify the frame layout and right justify text fields which might provide a nicer view for those who read right to left like Hebrew, Arabic and Persian.")
        )
        configdialog.add_checkbox(
            grid, _("Sort tags by name not priority"),
            11, "preferences.profile.person.layout.sort-tags-by-name",
            tooltip=_("Enabling this option will sort tags by name before displaying them. By default they sort by the priority in which they are organized in the tag organization tool.")
        )
        configdialog.add_checkbox(
            grid, _("Include notes on child objects"),
            12, "preferences.profile.person.layout.include-child-notes",
            tooltip=_("Enabling this option will include notes on children of the primary object in the Notes edit selection section of the action menu if any are present.")
        )
        configdialog.add_checkbox(
            grid, _("Enable warnings"),
            13, "preferences.profile.person.layout.enable-warnings",
            tooltip=_("Enabling this will raise a warning dialog asking for confirmation before performing an action that removes or deletes data as a safeguard.")
        )
        configdialog.add_checkbox(
            grid, _("Enable tooltips"),
            14, "preferences.profile.person.layout.enable-tooltips",
            tooltip=_("TBD TODO. If implemented some tooltips may be added to the view as an aid for new Gramps users which would quickly become annoying so this would turn them off for experienced users.")
        )
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.layout", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 20, 1, 1)
        return _("Layout"), grid

    def active_panel(self, configdialog):
        """
        Builds active person options section for the configuration dialog
        """
        grid = self.create_grid()        
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.person.active.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "preferences.profile.person.active.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "preferences.profile.person.active.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.person.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.person.active.tag-format",
            TAG_DISPLAY_MODES
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.person.active.tag-width",
            (1, 20)
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 8, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.active", 9)
        configdialog.add_text(grid, _("Extra Fact Display Fields"), 8, start=3, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.active", 9, start_col=3, extra=True)
        configdialog.add_text(grid, _("Metadata Display Fields"), 8, start=5, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.active", 9, start_col=5)
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.active", defaults=self.defaults, label=_("Reset Page Defaults"))
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
            1, "preferences.profile.person.parent.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "preferences.profile.person.parent.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "preferences.profile.person.parent.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Expand children by default"),
            2, "preferences.profile.person.parent.expand-children", start=3,
            tooltip=_("Enabling this option will automatically expand the list of children when the page is rendered.")
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.person.parent.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Matrilineal mode (inverts couple)"),
            3, "preferences.profile.person.parent.show-matrilineal", start=3,
            tooltip=_("Enabling this option will switch the placement of the male and female roles in the couple relationship.")
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.person.parent.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.person.parent.tag-width",
            (1, 20),
        )
        configdialog.add_checkbox(
            grid, _("Show divorce or divorce equivalent"),
            6, "preferences.profile.person.parent.show-divorce"
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.parent", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.parent", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.parent", defaults=self.defaults, label=_("Reset Page Defaults"))
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
            1, "preferences.profile.person.spouse.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "preferences.profile.person.spouse.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "preferences.profile.person.spouse.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Expand children by default"),
            2, "preferences.profile.person.spouse.expand-children", start=3,
            tooltip=_("Enabling this option will automatically expand the list of children when the page is rendered.")
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.person.spouse.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.person.spouse.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.person.spouse.tag-width",
            (1, 20),
        )
        configdialog.add_checkbox(
            grid, _("Show spouse only"),
            6, "preferences.profile.person.spouse.show-spouse-only",
        )
        configdialog.add_checkbox(
            grid, _("Show divorce or divorce equivalent"),
            6, "preferences.profile.person.spouse.show-divorce", start=3
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 13, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.spouse", 14)
        configdialog.add_text(grid, _("Metadata Display Fields"), 13, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.spouse", 14, start_col=3)
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.spouse", defaults=self.defaults, label=_("Reset Page Defaults"))
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
            1, "preferences.profile.person.child.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "preferences.profile.person.child.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "preferences.profile.person.child.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Number children"),
            2, "preferences.profile.person.child.number-children", start=3
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.person.child.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.person.child.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.person.child.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.child", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.child", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.child", defaults=self.defaults, label=_("Reset Page Defaults"))
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
            1, "preferences.profile.person.sibling.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            1, "preferences.profile.person.sibling.show-age", start=3
        )
        configdialog.add_combo(
            grid, _("Sex display mode"),
            2, "preferences.profile.person.sibling.sex-mode",
            SEX_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Number children"),
            2, "preferences.profile.person.sibling.number-children", start=3
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.person.sibling.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            4, "preferences.profile.person.sibling.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            5, "preferences.profile.person.sibling.tag-width",
            (1, 20),
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.sibling", 12)
        configdialog.add_text(grid, _("Metadata Display Fields"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.sibling", 12, start_col=3)
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.sibling", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 30, 1, 1)
        return _("Siblings"), grid

    def timeline_panel(self, configdialog):
        """
        Builds active person timeline options section for the configuration dialog
        """
        grid1 = self.create_grid()
        configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid1, _("Timeline color scheme"),
            1, "preferences.profile.person.timeline.color-scheme",
            TIMELINE_COLOR_MODES,
        )
        configdialog.add_combo(
            grid1, _("Tag display mode"),
            2, "preferences.profile.person.timeline.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid1, _("Maximum tags per line"),
            3, "preferences.profile.person.timeline.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid1, _("Image display mode"),
            4, "preferences.profile.person.timeline.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid1, _("Show year and age"),
            5, "preferences.profile.person.timeline.show-age",
            tooltip=_("Enabling this option will show the year of the event and the age of the active person at that time if it can be calculated.")
        )
        configdialog.add_text(grid1, _("Display Attributes"), 6, bold=True)
        configdialog.add_checkbox(
            grid1, _("Show role always not just secondary events"),
            7, "preferences.profile.person.timeline.show-role-always",
            tooltip=_("Enabling this option will always show the role of the active person in the event. This is normally implicit if they had none or they were the primary participant. Note their role is always displayed for secondary events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show description"),
            8, "preferences.profile.person.timeline.show-description",
            tooltip=_("Enabling this option will show the event description if one is available.")
        )
        configdialog.add_checkbox(
            grid1, _("Show registered participants if more than one person"),
            9, "preferences.profile.person.timeline.show-participants",
            tooltip=_("Enabling this option will show the other participants in shared events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show source count"),
            10, "preferences.profile.person.timeline.show-source-count",
            tooltip=_("Enabling this option will include a count of the number of unique sources cited from in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show citation count"),
            11, "preferences.profile.person.timeline.show-citation-count",
            tooltip=_("Enabling this option will include a count of the number of citations in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show best confidence rating"),
            12, "preferences.profile.person.timeline.show-best-confidence",
            tooltip=_("Enabling this option will show the highest user defined confidence rating found among all the citations in support of the information about the event.")
        )
        configdialog.add_text(grid1, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid1, "preferences.profile.person.timeline", 16, start_col=1, number=4, obj_type="Event")
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.timeline", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid1.attach(reset, 1, 25, 1, 1)
        grid2 = self.create_grid()
        configdialog.add_text(grid2, _("Category Filters"), 0, bold=True)
        configdialog.add_checkbox(
            grid2, _("Show vital"),
            1, "preferences.profile.person.timeline.show-class-vital",
            tooltip=_("Enabling this option will show all vital events for the person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others.")
        )
        configdialog.add_checkbox(
            grid2, _("Show family"),
            2, "preferences.profile.person.timeline.show-class-family",
            tooltip=_("Enabling this option will show all family related events for the active person on the timeline. The list of family events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show religious"),
            3, "preferences.profile.person.timeline.show-class-religious",
            tooltip=_("Enabling this option will show all religious events for the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show vocational"),
            4, "preferences.profile.person.timeline.show-class-vocational",
            tooltip=_("Enabling this option will show all vocational events for the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show academic"),
            5, "preferences.profile.person.timeline.show-class-academic",
            tooltip=_("Enabling this option will show all academic events for the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show travel"),
            6, "preferences.profile.person.timeline.show-class-travel",
            tooltip=_("Enabling this option will show all travel events for the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show legal"),
            7, "preferences.profile.person.timeline.show-class-legal",
            tooltip=_("Enabling this option will show all legal events for the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show residence"),
            8, "preferences.profile.person.timeline.show-class-residence",
            tooltip=_("Enabling this option will show all residence events for the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show other"),
            9, "preferences.profile.person.timeline.show-class-other",
            tooltip=_("Enabling this option will show all other events for the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show custom"),
            10, "preferences.profile.person.timeline.show-class-custom",
            tooltip=_("Enabling this option will show all user defined custom events for the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor.")
        )
        grid3 = self.create_grid()
        configdialog.add_text(grid3, _("Relationship Filters"), 0, bold=True)
        configdialog.add_spinner(
            grid3, _("Generations of ancestors to examine"),
            1, "preferences.profile.person.timeline.generations-ancestors",
            (1, 3),
        )
        configdialog.add_spinner(
            grid3, _("Generations of offspring to examine"),
            2, "preferences.profile.person.timeline.generations-offspring",
            (1, 3),
        )
        configdialog.add_checkbox(
            grid3, _("Include events for father and grandfathers"),
            3, "preferences.profile.person.timeline.show-family-father",
            tooltip=_("Enabling this option will include events for fathers, stepfathers, and grandfathers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for mother and grandmothers"),
            4, "preferences.profile.person.timeline.show-family-mother",
            tooltip=_("Enabling this option will include events for mothers, stepmothers, and grandmothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for brothers and stepbrothers"),
            5, "preferences.profile.person.timeline.show-family-brother",
            tooltip=_("Enabling this option will include events for brothers and stepbrothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for sisters and stepsisters"),
            6, "preferences.profile.person.timeline.show-family-sister",
            tooltip=_("Enabling this option will include events for sisters and stepsisters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for wives"),
            7, "preferences.profile.person.timeline.show-family-wife",
            tooltip=_("Enabling this option will include events for the wives of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for husbands"),
            8, "preferences.profile.person.timeline.show-family-husband",
            tooltip=_("Enabling this option will include events for the husbands of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for sons and grandsons"),
            9, "preferences.profile.person.timeline.show-family-son",
            tooltip=_("Enabling this option will include events for the sons and grandsons of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for daughters and granddaughters"),
            10, "preferences.profile.person.timeline.show-family-daughter",
            tooltip=_("Enabling this option will include events for the daughters and granddaughters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        grid4 = self.create_grid()
        configdialog.add_text(grid4, _("Relationship Category Filters"), 0, bold=True)
        configdialog.add_checkbox(
            grid4, _("Show vital"),
            1, "preferences.profile.person.timeline.show-family-class-vital",
            tooltip=_("Enabling this option will show all vital events for the eligible relations of the active person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others.")
        )
        configdialog.add_checkbox(
            grid4, _("Show family"),
            2, "preferences.profile.person.timeline.show-family-class-family",
            tooltip=_("Enabling this option will show all family related events for the eligible relations of the active person on the timeline. The list of family events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show religious"),
            3, "preferences.profile.person.timeline.show-family-class-religious",
            tooltip=_("Enabling this option will show all religious related events for the eligible relations of the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show vocational"),
            4, "preferences.profile.person.timeline.show-family-class-vocational",
            tooltip=_("Enabling this option will show all vocational related events for the eligible relations of the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show academic"),
            5, "preferences.profile.person.timeline.show-family-class-academic",
            tooltip=_("Enabling this option will show all academic related events for the eligible relations of the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show travel"),
            6, "preferences.profile.person.timeline.show-family-class-travel",
            tooltip=_("Enabling this option will show all travel related events for the eligible relations of the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show legal"),
            7, "preferences.profile.person.timeline.show-family-class-legal",
            tooltip=_("Enabling this option will show all legal related events for the eligible relations of the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show residence"),
            8, "preferences.profile.person.timeline.show-family-class-residence",
            tooltip=_("Enabling this option will show all residence related events for the eligible relations of the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show other"),
            9, "preferences.profile.person.timeline.show-family-class-other",
            tooltip=_("Enabling this option will show all other events for the eligible relations of the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show custom"),
            10, "preferences.profile.person.timeline.show-family-class-custom",
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
            1, "preferences.profile.person.citation.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "preferences.profile.person.citation.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.person.citation.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Sort citations by date"),
            4, "preferences.profile.person.citation.sort-by-date",
            tooltip=_("Enabling this option will sort the citations by date.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations about the person"),
            5, "preferences.profile.person.citation.include-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes like names and person associations in addition to the ones directly on the person themselves.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a child"),
            6, "preferences.profile.person.citation.include-parent-family",
            tooltip=_("Enabling this option will include citations related to the membership of the person as a child in other families.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a head of household"),
            7, "preferences.profile.person.citation.include-family",
            tooltip=_("Enabling this option will include citations on the families this person formed with other partners.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations related to the persons family membership as a head of household"),
            8, "preferences.profile.person.citation.include-family-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes about the families this person formed with other partners.")
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show date"),
            10, "preferences.profile.person.citation.show-date",
            tooltip=_("Enabling this option will show the citation date if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show publisher"),
            11, "preferences.profile.person.citation.show-publisher",
            tooltip=_("Enabling this option will show the publisher information if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference type"),
            12, "preferences.profile.person.citation.show-reference-type",
            tooltip=_("Enabling this option will display what type of citation it is. Direct is one related to the person or a family they formed, indirect would be related to some nested attribute like a name or person association.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference description"),
            13, "preferences.profile.person.citation.show-reference-description",
            tooltip=_("Enabling this option will display a description of the type of data the citation supports. For direct citations this would be person or family, indirect ones could be primary name, an attribute, association, address, and so forth.")
        )
        configdialog.add_checkbox(
            grid, _("Show confidence rating"),
            14, "preferences.profile.person.citation.show-confidence",
            tooltip=_("Enabling this option will display the user selected confidence level for the citation.")
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.citation", 16, start_col=1, number=4, obj_type="Citation")
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.citation", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Citations"), grid

    def media_panel(self, configdialog):
        """
        Builds media options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "preferences.profile.person.media.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "preferences.profile.person.media.tag-width",
            (1, 20),
        )
        configdialog.add_checkbox(
            grid, _("Sort media by date"),
            4, "preferences.profile.person.media.sort-by-date",
            tooltip=_("Enabling this option will sort the media by date.")
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show date"),
            10, "preferences.profile.person.media.show-date",
            tooltip=_("Enabling this option will show the media date if it is available.")
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.media", 16, start_col=1, number=4, obj_type="Media")
        reset = ConfigReset(configdialog, self.config, "preferences.profile.person.media", defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Media"), grid

    def color_panel(self, configdialog):
        """
        Add the tab to set defaults colors for graph boxes.
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("See global preferences for option to switch between light and dark color schemes"), 0, bold=True)
        configdialog.add_text(grid, _("The default Gramps person color scheme is also managed under global preferences"), 1, bold=True)

        color_type = [
            ('Confidence', _('Confidence color scheme'), "preferences.profile.colors.confidence"),
            ('Relation', _('Relationship color scheme'),"preferences.profile.colors.relations"),
            ('Event', _('Event category color scheme'), "preferences.profile.colors.events")
        ]

        # for confidence scheme
        bg_very_high_text = _('Background for Very High')
        bg_high_text = _('Background for High')
        bg_normal_text = _('Background for Normal')
        bg_low_text = _('Background for Low')
        bg_very_low_text = _('Background for Very Low')
        brd_very_high_text = _('Border for Very High')
        brd_high_text = _('Border for High')
        brd_normal_text = _('Border for Normal')
        brd_low_text = _('Border for Low')
        brd_very_low_text = _('Border for Very Low')

        # for relation scheme
        bg_active = _('Background for Active Person')
        bg_spouse = _('Background for Spouse')
        bg_father = _('Background for Father')
        bg_mother = _('Background for Mother')
        bg_brother = _('Background for Brother')
        bg_sister = _('Background for Sister')
        bg_son = _('Background for Son')
        bg_daughter = _('Background for Daughter')
        bg_none = _('Background for None')
        brd_active = _('Border for Active Person')
        brd_spouse = _('Border for Spouse')
        brd_father = _('Border for Father')
        brd_mother = _('Border for Mother')
        brd_brother = _('Border for Brother')
        brd_sister = _('Border for Sister')
        brd_son = _('Border for Son')
        brd_daughter = _('Border for Daughter')
        brd_none = _('Border for None')

        # for event category scheme
        bg_vital = _('Background for Vital Events')
        bg_family = _('Background for Family Events')
        bg_religious = _('Background for Religious Events')
        bg_vocational = _('Background for Vocational Events')
        bg_academic = _('Background for Academic Events')
        bg_travel = _('Background for Travel Events')
        bg_legal = _('Background for Legal Events')
        bg_residence = _('Background for Residence Events')
        bg_other = _('Background for Other Events')
        bg_custom = _('Background for Custom Events')
        brd_vital = _('Border for Vital Events')
        brd_family = _('Border for Family Events')
        brd_religious = _('Border for Religious Events')
        brd_vocational = _('Border for Vocational Events')
        brd_academic = _('Border for Academic Events')
        brd_travel = _('Border for Travel Events')
        brd_legal = _('Border for Legal Events')
        brd_residence = _('Border for Residence Events')
        brd_other = _('Border for Other Events')
        brd_custom = _('Border for Custom Events')
        
        # color label, config constant, group grid row, column, color type
        color_list = [
            # for confidence scheme
            (bg_very_high_text, 'preferences.profile.colors.confidence.very-high', 1, 1, 'Confidence'),
            (bg_high_text, 'preferences.profile.colors.confidence.high', 2, 1, 'Confidence'),
            (bg_normal_text, 'preferences.profile.colors.confidence.normal', 3, 1, 'Confidence'),
            (bg_low_text, 'preferences.profile.colors.confidence.low', 4, 1, 'Confidence'),
            (bg_very_low_text, 'preferences.profile.colors.confidence.very-low', 5, 1, 'Confidence'),
            (brd_very_high_text, 'preferences.profile.colors.confidence.border-very-high', 1, 4, 'Confidence'),
            (brd_high_text, 'preferences.profile.colors.confidence.border-high', 2, 4, 'Confidence'),
            (brd_normal_text, 'preferences.profile.colors.confidence.border-normal', 3, 4, 'Confidence'),
            (brd_low_text, 'preferences.profile.colors.confidence.border-low', 4, 4, 'Confidence'),
            (brd_very_low_text, 'preferences.profile.colors.confidence.border-very-low', 5, 4, 'Confidence'),

            # for relation scheme
            (bg_active, 'preferences.profile.colors.relations.active', 1, 1, 'Relation'),
            (bg_spouse, 'preferences.profile.colors.relations.spouse', 2, 1, 'Relation'),
            (bg_father, 'preferences.profile.colors.relations.father', 3, 1, 'Relation'),
            (bg_mother, 'preferences.profile.colors.relations.mother', 4, 1, 'Relation'),
            (bg_brother, 'preferences.profile.colors.relations.brother', 5, 1, 'Relation'),
            (bg_sister, 'preferences.profile.colors.relations.sister', 6, 1, 'Relation'),
            (bg_son, 'preferences.profile.colors.relations.son', 7, 1, 'Relation'),
            (bg_daughter, 'preferences.profile.colors.relations.daughter', 8, 1, 'Relation'),
            (bg_none, 'preferences.profile.colors.relations.none', 9, 1, 'Relation'),
            (brd_active, 'preferences.profile.colors.relations.border-active', 1, 4, 'Relation'),
            (brd_spouse, 'preferences.profile.colors.relations.border-spouse', 2, 4, 'Relation'),
            (brd_father, 'preferences.profile.colors.relations.border-father', 3, 4, 'Relation'),
            (brd_mother, 'preferences.profile.colors.relations.border-mother', 4, 4, 'Relation'),
            (brd_brother, 'preferences.profile.colors.relations.border-brother', 5, 4, 'Relation'),
            (brd_sister, 'preferences.profile.colors.relations.border-sister', 6, 4, 'Relation'),
            (brd_son, 'preferences.profile.colors.relations.border-son', 7, 4, 'Relation'),
            (brd_daughter, 'preferences.profile.colors.relations.border-daughter', 8, 4, 'Relation'),
            (brd_none, 'preferences.profile.colors.relations.border-none', 9, 4, 'Relation'),

            # for event category scheme
            (bg_vital, 'preferences.profile.colors.events.vital', 1, 1, 'Event'),
            (bg_family, 'preferences.profile.colors.events.family', 2, 1, 'Event'),
            (bg_religious, 'preferences.profile.colors.events.religious', 3, 1, 'Event'),
            (bg_vocational, 'preferences.profile.colors.events.vocational', 4, 1, 'Event'),
            (bg_academic, 'preferences.profile.colors.events.academic', 5, 1, 'Event'),
            (bg_travel, 'preferences.profile.colors.events.travel', 6, 1, 'Event'),
            (bg_legal, 'preferences.profile.colors.events.legal', 7, 1, 'Event'),
            (bg_residence, 'preferences.profile.colors.events.residence', 8, 1, 'Event'),
            (bg_other, 'preferences.profile.colors.events.other', 9, 1, 'Event'),
            (bg_custom, 'preferences.profile.colors.events.custom', 10, 1, 'Event'),
            (brd_vital, 'preferences.profile.colors.events.border-vital', 1, 4, 'Event'),
            (brd_family, 'preferences.profile.colors.events.border-family', 2, 4, 'Event'),
            (brd_religious, 'preferences.profile.colors.events.border-religious', 3, 4, 'Event'),
            (brd_vocational, 'preferences.profile.colors.events.border-vocational', 4, 4, 'Event'),
            (brd_academic, 'preferences.profile.colors.events.border-academic', 5, 4, 'Event'),
            (brd_travel, 'preferences.profile.colors.events.border-travel', 6, 4, 'Event'),
            (brd_legal, 'preferences.profile.colors.events.border-legal', 7, 4, 'Event'),
            (brd_residence, 'preferences.profile.colors.events.border-residence', 8, 4, 'Event'),
            (brd_other, 'preferences.profile.colors.events.border-other', 9, 4, 'Event'),
            (brd_custom, 'preferences.profile.colors.events.border-custom', 10, 4, 'Event'),
            ]

        # prepare scrolled window for colors settings
        scroll_window = Gtk.ScrolledWindow()
        colors_grid = self.create_grid()
        scroll_window.add(colors_grid)
        scroll_window.set_vexpand(True)
        scroll_window.set_policy(Gtk.PolicyType.NEVER,
                                 Gtk.PolicyType.AUTOMATIC)
        grid.attach(scroll_window, 0, 3, 7, 1)

        # add color settings to scrolled window by groups
        row = 0
        self.colors = {}
        for key, frame_lbl, space in color_type:
            group_label = Gtk.Label()
            group_label.set_halign(Gtk.Align.START)
            group_label.set_margin_top(12)
            group_label.set_markup(_('<b>%s</b>') % frame_lbl)
            colors_grid.attach(group_label, 0, row, 2, 1)

            row_added = 0
            for color in color_list:
                if color[4] == key:
                    pref_name = color[1]
                    self.colors[pref_name] = self.add_color(
                        colors_grid, color[0], row + color[2],
                        pref_name, col=color[3])
                    row_added += 1
            row += row_added + 1
        return _('Colors'), grid

    def _get_configure_page_funcs(self):
        """
        Return the list of functions for generating the configuration dialog notebook pages.
        """
        return [
            self.layout_panel,
            self.color_panel,
            self.active_panel,
            self.parents_panel,
            self.siblings_panel,
            self.spouses_panel,
            self.children_panel,
            self.timeline_panel,
            self.citations_panel,
            self.media_panel,
        ]

    def edit_active(self, *obj):
        if self.active_profile:
            self.active_profile.edit_object()

    def add_spouse(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_spouse()

    def select_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_existing_parents()

    def add_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_parents()

    def add_tag(self, trans, object_handle, tag_handle):
        if self.active_profile:
            self.active_profile.add_tag(trans, object_handle, tag_handle)
