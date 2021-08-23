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
Page utility functions
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
from ..frames.frame_utils import ConfigReset
from ..frames.frame_selectors import AttributeSelector, FrameFieldSelector
from .page_const import TAG_DISPLAY_MODES

_ = glocale.translation.sgettext


def create_grid():
    """
    Generate grid for config panels.
    """
    grid = Gtk.Grid(row_spacing=6, column_spacing=6, column_homogeneous=False, margin_bottom=12)
    return grid


def add_config_reset(configdialog, grstate, space, grid):
    """
    Add configuration reset option for grid options.
    """
    vbox = Gtk.VBox(margin=12)
    vbox.pack_start(grid, True, True, 0)
    reset = ConfigReset(configdialog, grstate, space)
    vbox.pack_end(reset, False, False, 0)
    return vbox


def config_facts_fields(
    configdialog,
    grstate,
    space,
    person,
    grid,
    start_row,
    start_col=1,
    number=8,
    extra=False,
):
    """
    Build facts field configuration section.
    """
    count = 1
    row = start_row
    key = "facts-field"
    if extra:
        key = "extra-field"
    while row < start_row + number:
        option = "{}.{}.{}-{}".format(space, person, key, count)
        user_select = FrameFieldSelector(
            option,
            grstate.config,
            grstate.dbstate,
            grstate.uistate,
            count,
            dbid=True,
        )
        grid.attach(user_select, start_col, row, 2, 1)
        count = count + 1
        row = row + 1
    option = "{}.{}.{}-skip-birth-alternates".format(space, person, key)
    configdialog.add_checkbox(
        grid,
        _("Skip birth alternatives if birth found"),
        row,
        option,
        start=start_col,
        stop=start_col + 1,
        tooltip=_(
            "If enabled then if a birth event was found other events considered to be birth alternatives such as baptism or christening will not be displayed."
        ),
    )
    row = row + 1
    option = "{}.{}.{}-skip-death-alternates".format(space, person, key)
    configdialog.add_checkbox(
        grid,
        _("Skip death alternates if death found"),
        row,
        option,
        start=start_col,
        stop=start_col + 1,
        tooltip=_(
            "If enabled then if a death event was found other events considered to be death alternatives such as burial or cremation will not be displayed."
        ),
    )
    row = row + 1


def config_metadata_attributes(
    grstate,
    space,
    grid,
    start_row,
    start_col=1,
    number=8,
    obj_selector_type="Person",
):
    """
    Build metadata display field configuration section.
    """
    count = 1
    row = start_row
    while row < start_row + number:
        option = "{}.metadata-attribute-{}".format(
            space, count
        )
        attr_select = AttributeSelector(
            option,
            grstate.config,
            grstate.dbstate.db,
            obj_selector_type,
            dbid=True,
            tooltip=_(
                "This option allows you to select the name of an attribute. The value of the attribute, if one is found, will then be displayed in the metadata section of the frame beneath the Gramps Id."
            ),
        )
        label = Gtk.Label(
            halign=Gtk.Align.START,
            label="{} {}: ".format(_("Field"), count),
        )
        grid.attach(label, start_col, row, 1, 1)
        grid.attach(attr_select, start_col + 1, row, 1, 1)
        count = count + 1
        row = row + 1


def config_tag_fields(configdialog, space, grid, start_row):
    """
    Build tag display configuration section.
    """
    configdialog.add_combo(
        grid,
        _("Tag display mode"),
        start_row,
        "{}.tag-format".format(space),
        TAG_DISPLAY_MODES,
    )
    configdialog.add_spinner(
        grid,
        _("Maximum tags per line"),
        start_row + 1,
        "{}.tag-width".format(space),
        (1, 20),
    )
