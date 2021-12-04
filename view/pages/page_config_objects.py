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
Page configuration dialog functions
"""

# -------------------------------------------------------------------------
#
# Gnome/Gtk Modules
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
from .page_const import (
    EVENT_COLOR_MODES,
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    MEDIA_IMAGE_DISPLAY_MODES,
    REF_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
)
from .page_utils import add_config_reset, config_facts_fields, create_grid

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# ConfigNotebook class
#
# -------------------------------------------------------------------------
class ConfigNotebook(Gtk.Notebook):
    """
    Provide a Notebook with deferred tab rendering support.
    """

    def __init__(self, vexpand=True, hexpand=True):
        Gtk.Notebook.__init__(self, vexpand=vexpand, hexpand=hexpand)
        self.set_tab_pos(Gtk.PositionType.LEFT)
        self.deferred_pages = {}
        self.rendered_pages = []
        self.connect("switch-page", self.handle_page_switch)

    def append_deferred_page(self, tab_label, render_page):
        """
        Appends a page deferring rendering till selected.
        """
        container = Gtk.HBox()
        index = self.append_page(container, tab_label=tab_label)
        self.deferred_pages.update({index: (container, render_page)})

    def handle_page_switch(self, widget, _dummy_tab, index):
        """
        Handle a page switch, rendering the page if needed.
        """
        if widget == self:
            if index not in self.rendered_pages:
                if index in self.deferred_pages:
                    container, render_page = self.deferred_pages[index]
                    page = render_page()
                    container.pack_start(page, True, True, 0)
                    container.show_all()
                    self.rendered_pages.append(index)


def build_person_grid(configdialog, grstate, space, person, extra=False):
    """
    Builds a person options section for the configuration dialog
    """
    grid = create_grid()
    grid1 = create_grid()
    configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid1,
        _("Event display format"),
        1,
        "{}.{}.event-format".format(space, person),
        EVENT_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Show age at death and if selected burial or if living"),
        2,
        "{}.{}.show-age".format(space, person),
    )
    configdialog.add_combo(
        grid1,
        _("Sex display mode"),
        3,
        "{}.{}.sex-mode".format(space, person),
        SEX_DISPLAY_MODES,
    )
    configdialog.add_combo(
        grid1,
        _("Image display mode"),
        4,
        "{}.{}.image-mode".format(space, person),
        IMAGE_DISPLAY_MODES,
    )
    if "group" in space and person in ["child", "sibling", "association"]:
        configdialog.add_combo(
            grid1,
            _("Reference display mode"),
            7,
            "{}.{}.reference-mode".format(space, person),
            REF_DISPLAY_MODES,
        )
    grid.attach(grid1, 0, 0, 1, 1)

    grid2a = create_grid()
    configdialog.add_text(grid2a, _("Primary Fact Group"), 0, bold=True)
    config_facts_fields(configdialog, grstate, space, person, grid2a, 1)
    grid.attach(grid2a, 0, 1, 1, 1)

    grid2b = create_grid()
    configdialog.add_text(grid2b, _("Attributes Group"), 0, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        person,
        grid2b,
        1,
        mode="fact",
        key="attributes-field",
    )
    grid.attach(grid2b, 1, 1, 1, 1)

    grid3 = create_grid()
    if extra:
        configdialog.add_text(grid3, _("Secondary Fact Group"), 0, bold=True)
        config_facts_fields(
            configdialog,
            grstate,
            space,
            person,
            grid3,
            1,
            key="extra-field",
        )
    grid.attach(grid3, 0, 2, 1, 1)
    return add_config_reset(
        configdialog, grstate, "{}.{}".format(space, person), grid
    )


def build_family_grid(configdialog, grstate, space):
    """
    Builds a family options section for the configuration dialog
    """
    grid = create_grid()
    grid1 = create_grid()
    configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid1,
        _("Event display format"),
        1,
        "{}.family.event-format".format(space),
        EVENT_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Show years married at divorce and if selected annulment"),
        2,
        "{}.family.show-years".format(space),
    )
    configdialog.add_combo(
        grid1,
        _("Image display mode"),
        3,
        "{}.family.image-mode".format(space),
        IMAGE_DISPLAY_MODES,
    )
    if "group" in space:
        configdialog.add_checkbox(
            grid1,
            _("When on person page only show the spouse in family groups"),
            6,
            "{}.family.show-spouse-only".format(space),
        )
    configdialog.add_checkbox(
        grid1,
        _("Matrilineal mode, display female partner first"),
        7,
        "{}.family.show-matrilineal".format(space),
        start=1,
    )
    configdialog.add_checkbox(
        grid1,
        _("Show relationship if related"),
        8,
        "{}.family.show-relationship".format(space),
        start=1,
    )
    grid.attach(grid1, 0, 0, 1, 1)

    grid2a = create_grid()
    configdialog.add_text(grid2a, _("Primary Fact Group"), 0, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "family",
        grid2a,
        1,
        mode="event",
        obj_type="Family",
    )
    grid.attach(grid2a, 0, 1, 1, 1)

    grid2b = create_grid()
    configdialog.add_text(grid2b, _("Attributes Group"), 0, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "family",
        grid2b,
        1,
        mode="fact",
        key="attributes-field",
        obj_type="Family",
    )
    grid.attach(grid2b, 1, 1, 1, 1)

    grid3 = create_grid()
    if "active" in space:
        configdialog.add_text(grid3, _("Secondary Fact Group"), 0, bold=True)
        config_facts_fields(
            configdialog,
            grstate,
            space,
            "family",
            grid3,
            1,
            mode="event",
            key="extra-field",
            obj_type="Family",
        )
    grid.attach(grid3, 0, 2, 1, 1)
    return add_config_reset(
        configdialog, grstate, "{}.family".format(space), grid
    )


def build_name_grid(configdialog, grstate, space, group=True):
    """
    Builds a name options section for the configuration dialog
    """
    grid = create_grid()
    if group:
        configdialog.add_text(grid, _("Group Display Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid,
            _("Show year and age"),
            1,
            "{}.name.show-age".format(space),
            tooltip=_(
                "Valid when name is for a person. If name is "
                "dated will show year and age of person on that "
                "date."
            ),
        )
    return add_config_reset(
        configdialog, grstate, "{}.name".format(space), grid
    )


def build_ldsord_grid(configdialog, grstate, space, group=True):
    """
    Builds a ordinance options section for the configuration dialog
    """
    grid = create_grid()
    if group:
        configdialog.add_text(grid, _("Group Display Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid,
            _("Show year and age"),
            1,
            "{}.ldsord.show-age".format(space),
            tooltip=_(
                "Valid when ordinance is for a person. If ordinance "
                "is dated will show year and age of person on that "
                "date."
            ),
        )
    return add_config_reset(
        configdialog, grstate, "{}.ldsord".format(space), grid
    )


def build_address_grid(configdialog, grstate, space, group=True):
    """
    Builds an address options section for the configuration dialog
    """
    grid = create_grid()
    if group:
        configdialog.add_text(grid, _("Group Display Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid,
            _("Show year and age"),
            1,
            "{}.address.show-age".format(space),
            tooltip=_(
                "Valid when address is for a person. If address is "
                "dated will show year and age of person on that "
                "date."
            ),
        )
    return add_config_reset(
        configdialog, grstate, "{}.address".format(space), grid
    )


def build_media_grid(configdialog, grstate, space, group=True):
    """
    Builds a media options section for the configuration dialog
    """
    grid = create_grid()
    if group:
        configdialog.add_text(grid, _("Group Display Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid,
            _("Show year and age"),
            1,
            "{}.media.show-age".format(space),
            tooltip=_(
                "Valid when media is for a person. If media is "
                "dated will show year and age of person on that "
                "date."
            ),
        )
        configdialog.add_checkbox(
            grid,
            _("Sort media by date"),
            2,
            "{}.media.sort-by-date".format(space),
            tooltip=_("Indicates whether to sort media items by date."),
        )
        configdialog.add_checkbox(
            grid,
            _("Group media by type"),
            3,
            "{}.media.group-by-type".format(space),
            tooltip=_(
                "Indicates whether to group like media, based on the "
                "custom Media-Type attribute."
            ),
        )
        configdialog.add_checkbox(
            grid,
            _("Filter out non-photos"),
            4,
            "{}.media.filter-non-photos".format(space),
            tooltip=_(
                "Indicates only photos should be displayed, based on "
                "the custom Media-Type attribute."
            ),
        )
    configdialog.add_text(grid, _("Object Display Options"), 10, bold=True)
    configdialog.add_combo(
        grid,
        _("Image display mode"),
        12,
        "{}.media.image-mode".format(space),
        MEDIA_IMAGE_DISPLAY_MODES,
    )
    if "group" in space:
        configdialog.add_combo(
            grid,
            _("Reference display mode"),
            13,
            "{}.media.reference-mode".format(space),
            REF_DISPLAY_MODES,
        )
    configdialog.add_checkbox(
        grid,
        _("Show date"),
        15,
        "{}.media.show-date".format(space),
        stop=2,
        tooltip=_(
            "Enabling this option will show the media date if it is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show path"),
        16,
        "{}.media.show-path".format(space),
        stop=2,
        tooltip=_(
            "Enabling this option will show the media file path if it is "
            "available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show mime type"),
        17,
        "{}.media.show-mime-type".format(space),
        stop=2,
        tooltip=_(
            "Enabling this option will show the media mime type if it is "
            "available."
        ),
    )
    configdialog.add_text(grid, _("Attributes Group"), 20, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "media",
        grid,
        21,
        start_col=1,
        number=4,
        mode="fact",
        key="attributes-field",
        obj_type="Media",
    )
    return add_config_reset(
        configdialog, grstate, "{}.media".format(space), grid
    )


def build_note_grid(configdialog, grstate, space):
    """
    Builds note options section for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Text on top"),
        1,
        "{}.note.text-on-top".format(space),
        tooltip=_(
            "Indicates text should be shown first and then title and metadata."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Enable preview mode"),
        2,
        "{}.note.preview-mode".format(space),
        tooltip=_(
            "Indicates only a portion of the full note should be displayed."
        ),
    )
    configdialog.add_spinner(
        grid,
        _("Number of lines to preview"),
        3,
        "{}.note.preview-lines".format(space),
        (0, 8),
    )
    return add_config_reset(
        configdialog, grstate, "{}.note".format(space), grid
    )


def build_citation_grid(configdialog, grstate, space):
    """
    Builds citation options section for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid,
        _("Image display mode"),
        1,
        "{}.citation.image-mode".format(space),
        IMAGE_DISPLAY_MODES,
    )
    configdialog.add_checkbox(
        grid,
        _("Show year and age"),
        2,
        "{}.citation.show-age".format(space),
        tooltip=_(
            "Valid when citation is for a person. If citation "
            "is dated will show year and age of person on that "
            "date."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Sort citations by date"),
        4,
        "{}.citation.sort-by-date".format(space),
        tooltip=_("Enabling this option will sort the citations by date."),
    )
    configdialog.add_checkbox(
        grid,
        _("Include indirect citations about the person"),
        5,
        "{}.citation.include-indirect".format(space),
        tooltip=_(
            "Enabling this option will include citations on nested "
            "attributes like names and person associations in addition "
            "to the ones directly on the person themselves."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include citations related to the persons family membership "
            "as a child"
        ),
        6,
        "{}.citation.include-parent-family".format(space),
        tooltip=_(
            "Enabling this option will include citations related to the "
            "membership of the person as a child in other families."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include citations related to the persons family membership "
            "as a head of household"
        ),
        7,
        "{}.citation.include-family".format(space),
        tooltip=_(
            "Enabling this option will include citations on the families "
            "this person formed with other partners."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include indirect citations related to the persons family "
            "membership as a head of household"
        ),
        8,
        "{}.citation.include-family-indirect".format(space),
        tooltip=_(
            "Enabling this option will include citations on nested "
            "attributes about the families this person formed with "
            "other partners."
        ),
    )
    configdialog.add_text(grid, _("Attributes"), 9, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Show date"),
        10,
        "{}.citation.show-date".format(space),
        tooltip=_(
            "Enabling this option will show the citation date if it is "
            "available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show publisher"),
        11,
        "{}.citation.show-publisher".format(space),
        tooltip=_(
            "Enabling this option will show the publisher information if it "
            "is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show reference type"),
        12,
        "{}.citation.show-reference-type".format(space),
        tooltip=_(
            "Enabling this option will display what type of citation it is. "
            "Direct is one related to the person or a family they formed, "
            "indirect would be related to some nested attribute like a name "
            "or person association."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show reference description"),
        13,
        "{}.citation.show-reference-description".format(space),
        tooltip=_(
            "Enabling this option will display a description of the type of "
            "data the citation supports. For direct citations this would be "
            "person or family, indirect ones could be primary name, an "
            "attribute, association, address, and so forth."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show confidence rating"),
        14,
        "{}.citation.show-confidence".format(space),
        tooltip=_(
            "Enabling this option will display the user selected confidence "
            "level for the citation."
        ),
    )
    configdialog.add_text(grid, _("Attributes Group"), 15, start=1, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "citation",
        grid,
        16,
        start_col=1,
        number=4,
        mode="fact",
        key="attributes-field",
        obj_type="Citation",
    )
    return add_config_reset(
        configdialog, grstate, "{}.citation".format(space), grid
    )


def build_source_grid(configdialog, grstate, space):
    """
    Builds source options section for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid,
        _("Event display format"),
        1,
        "{}.source.event-format".format(space),
        EVENT_DISPLAY_MODES,
    )
    configdialog.add_combo(
        grid,
        _("Image display mode"),
        3,
        "{}.source.image-mode".format(space),
        IMAGE_DISPLAY_MODES,
    )
    configdialog.add_text(grid, _("Attributes Group"), 15, start=1, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "source",
        grid,
        16,
        start_col=1,
        number=4,
        mode="fact",
        key="attributes-field",
        obj_type="Source",
    )
    return add_config_reset(
        configdialog, grstate, "{}.source".format(space), grid
    )


def build_repository_grid(configdialog, grstate, space):
    """
    Builds repository options section for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    if "group" in space:
        configdialog.add_combo(
            grid,
            _("Reference display mode"),
            3,
            "{}.repository.reference-mode".format(space),
            REF_DISPLAY_MODES,
        )
    configdialog.add_text(grid, _("Attributes"), 9, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Show call number"),
        10,
        "{}.repository.show-call-number".format(space),
        tooltip=_(
            "Enabling this option will show the source call number at the "
            "repository if it is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show media type"),
        11,
        "{}.repository.show-media-type".format(space),
        tooltip=_(
            "Enabling this option will show the source media type at the "
            "repository if it is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show repository type"),
        12,
        "{}.repository.show-repository-type".format(space),
        tooltip=_(
            "Enabling this option will show the repository type if it "
            "is available."
        ),
    )
    return add_config_reset(
        configdialog, grstate, "{}.repository".format(space), grid
    )


def build_place_grid(configdialog, grstate, space):
    """
    Builds place options section for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    return add_config_reset(
        configdialog, grstate, "{}.place".format(space), grid
    )


def build_event_grid(configdialog, grstate, space):
    """
    Builds event options section for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    configdialog.add_combo(
        grid,
        _("Event color scheme"),
        1,
        "{}.event.color-scheme".format(space),
        EVENT_COLOR_MODES,
    )
    configdialog.add_combo(
        grid,
        _("Event display format"),
        2,
        "{}.event.event-format".format(space),
        EVENT_DISPLAY_MODES,
    )
    configdialog.add_combo(
        grid,
        _("Image display mode"),
        3,
        "{}.event.image-mode".format(space),
        IMAGE_DISPLAY_MODES,
    )
    if "group" in space:
        configdialog.add_combo(
            grid,
            _("Reference display mode"),
            4,
            "{}.event.reference-mode".format(space),
            REF_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid,
            _("Show year and age"),
            5,
            "{}.event.show-age".format(space),
            tooltip=_(
                "Valid when event is for a person. If event "
                "is dated will show year and age of person on that "
                "date."
            ),
        )
    configdialog.add_text(grid, _("Display Attributes"), 12, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Show role always not just secondary events"),
        13,
        "{}.event.show-role-always".format(space),
        tooltip=_(
            "Enabling this option will always show the role of the active "
            "person in the event. This is normally implicit if they had none "
            "or they were the primary participant. Note their role is always "
            "displayed for secondary events."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show description"),
        14,
        "{}.event.show-description".format(space),
        tooltip=_(
            "Enabling this option will show the event description if one is "
            "available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show registered participants if more than one person"),
        15,
        "{}.event.show-participants".format(space),
        tooltip=_(
            "Enabling this option will show the other participants in shared "
            "events."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show source count"),
        16,
        "{}.event.show-source-count".format(space),
        tooltip=_(
            "Enabling this option will include a count of the number of "
            "unique sources cited from in support of the information about "
            "the event."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show citation count"),
        17,
        "{}.event.show-citation-count".format(space),
        tooltip=_(
            "Enabling this option will include a count of the number of "
            "citations in support of the information about the event."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show best confidence rating"),
        18,
        "{}.event.show-best-confidence".format(space),
        tooltip=_(
            "Enabling this option will show the highest user defined "
            "confidence rating found among all the citations in support of "
            "the information about the event."
        ),
    )
    configdialog.add_text(grid, _("Attributes Group"), 31, start=1, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "event",
        grid,
        32,
        start_col=1,
        number=4,
        mode="fact",
        key="attributes-field",
        obj_type="Event",
    )
    return add_config_reset(
        configdialog, grstate, "{}.event".format(space), grid
    )
