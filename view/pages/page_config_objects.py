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
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    MEDIA_IMAGE_DISPLAY_MODES,
    SEX_DISPLAY_MODES,
)
from .page_utils import (
    add_config_reset,
    config_facts_fields,
    config_tag_fields,
    create_grid,
)

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

    def handle_page_switch(self, widget, tab, index):
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
    config_tag_fields(configdialog, "{}.{}".format(space, person), grid1, 5)
    grid.attach(grid1, 0, 0, 1, 1)

    grid2A = create_grid()
    configdialog.add_text(grid2A, _("Primary Fact Group"), 0, bold=True)
    config_facts_fields(configdialog, grstate, space, person, grid2A, 1)
    grid.attach(grid2A, 0, 1, 1, 1)

    grid2B = create_grid()
    configdialog.add_text(grid2B, _("Attributes Group"), 0, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        person,
        grid2B,
        1,
        mode="fact",
        key="attributes-field",
    )
    grid.attach(grid2B, 1, 1, 1, 1)

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


def build_family_grid(configdialog, grstate, space, extra=False):
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
    config_tag_fields(configdialog, "{}.family".format(space), grid1, 4)
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
    grid.attach(grid1, 0, 0, 1, 1)

    grid2A = create_grid()
    configdialog.add_text(grid2A, _("Primary Fact Group"), 0, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "family",
        grid2A,
        1,
        mode="event",
        obj_type="Family",
    )
    grid.attach(grid2A, 0, 1, 1, 1)

    grid2B = create_grid()
    configdialog.add_text(grid2B, _("Attributes Group"), 0, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "family",
        grid2B,
        1,
        mode="fact",
        key="attributes-field",
        obj_type="Family",
    )
    grid.attach(grid2B, 1, 1, 1, 1)

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


def build_media_grid(configdialog, grstate, space, group=True):
    """
    Builds a media options section for the configuration dialog
    """
    grid = create_grid()
    if group:
        configdialog.add_text(grid, _("Group Display Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid,
            _("Sort media by date"),
            1,
            "{}.media.sort-by-date".format(space),
            tooltip=_("Indicates whether to sort media items by date."),
        )
        configdialog.add_checkbox(
            grid,
            _("Group media by type"),
            2,
            "{}.media.group-by-type".format(space),
            tooltip=_(
                "Indicates whether to group like media, based on Media-Type."
            ),
        )
        configdialog.add_checkbox(
            grid,
            _("Filter out non-photos"),
            3,
            "{}.media.filter-non-photos".format(space),
            tooltip=_(
                "Indicates only photos should be displayed, based on Media-Type."
            ),
        )
    configdialog.add_text(grid, _("Object Display Options"), 10, bold=True)
    configdialog.add_combo(
        grid,
        _("Image display mode"),
        11,
        "{}.media.image-mode".format(space),
        MEDIA_IMAGE_DISPLAY_MODES,
    )
    config_tag_fields(configdialog, "{}.media".format(space), grid, 12)
    configdialog.add_checkbox(
        grid,
        _("Show date"),
        14,
        "{}.media.show-date".format(space),
        stop=2,
        tooltip=_(
            "Enabling this option will show the media date if it is available."
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
        _("Enable preview mode"),
        1,
        "{}.note.preview-mode".format(space),
        tooltip=_(
            "Indicates only a portion of the full note should be displayed."
        ),
    )
    configdialog.add_spinner(
        grid,
        _("Number of lines to preview"),
        2,
        "{}.note.preview-lines".format(space),
        (0, 8),
    )
    config_tag_fields(configdialog, "{}.note".format(space), grid, 3)
    return add_config_reset(
        configdialog, grstate, "{}.note".format(space), grid
    )


def build_citation_grid(configdialog, grstate, space):
    """
    Builds citation options section for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("Display Options"), 0, bold=True)
    config_tag_fields(configdialog, "{}.citation".format(space), grid, 1)
    configdialog.add_combo(
        grid,
        _("Image display mode"),
        3,
        "{}.citation.image-mode".format(space),
        IMAGE_DISPLAY_MODES,
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
            "Enabling this option will include citations on nested attributes like names and person associations in addition to the ones directly on the person themselves."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include citations related to the persons family membership as a child"
        ),
        6,
        "{}.citation.include-parent-family".format(space),
        tooltip=_(
            "Enabling this option will include citations related to the membership of the person as a child in other families."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include citations related to the persons family membership as a head of household"
        ),
        7,
        "{}.citation.include-family".format(space),
        tooltip=_(
            "Enabling this option will include citations on the families this person formed with other partners."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _(
            "Include indirect citations related to the persons family membership as a head of household"
        ),
        8,
        "{}.citation.include-family-indirect".format(space),
        tooltip=_(
            "Enabling this option will include citations on nested attributes about the families this person formed with other partners."
        ),
    )
    configdialog.add_text(grid, _("Attributes"), 9, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Show date"),
        10,
        "{}.citation.show-date".format(space),
        tooltip=_(
            "Enabling this option will show the citation date if it is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show publisher"),
        11,
        "{}.citation.show-publisher".format(space),
        tooltip=_(
            "Enabling this option will show the publisher information if it is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show reference type"),
        12,
        "{}.citation.show-reference-type".format(space),
        tooltip=_(
            "Enabling this option will display what type of citation it is. Direct is one related to the person or a family they formed, indirect would be related to some nested attribute like a name or person association."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show reference description"),
        13,
        "{}.citation.show-reference-description".format(space),
        tooltip=_(
            "Enabling this option will display a description of the type of data the citation supports. For direct citations this would be person or family, indirect ones could be primary name, an attribute, association, address, and so forth."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show confidence rating"),
        14,
        "{}.citation.show-confidence".format(space),
        tooltip=_(
            "Enabling this option will display the user selected confidence level for the citation."
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
    config_tag_fields(configdialog, "{}.source".format(space), grid, 4)
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
    config_tag_fields(configdialog, "{}.repository".format(space), grid, 1)
    configdialog.add_text(grid, _("Attributes"), 9, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Show call number"),
        10,
        "{}.repository.show-call-number".format(space),
        tooltip=_(
            "Enabling this option will show the source call number at the repository if it is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show media type"),
        11,
        "{}.repository.show-media-type".format(space),
        tooltip=_(
            "Enabling this option will show the source media type at the repository if it is available."
        ),
    )
    configdialog.add_checkbox(
        grid,
        _("Show repository type"),
        12,
        "{}.repository.show-repository-type".format(space),
        tooltip=_(
            "Enabling this option will show the repository type if it is available."
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
    config_tag_fields(configdialog, "{}.place".format(space), grid, 4)
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
        _("Event display format"),
        1,
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
    config_tag_fields(configdialog, "{}.event".format(space), grid, 4)
    configdialog.add_text(grid, _("Attributes Group"), 11, start=1, bold=True)
    config_facts_fields(
        configdialog,
        grstate,
        space,
        "event",
        grid,
        16,
        start_col=1,
        number=4,
        mode="fact",
        key="attributes-field",
        obj_type="Event",
    )
    return add_config_reset(
        configdialog, grstate, "{}.event".format(space), grid
    )
