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

from ..frames.frame_selectors import FrameFieldSelector

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames.frame_utils import ConfigReset
from .page_const import TAG_DISPLAY_MODES

_ = glocale.translation.sgettext


def create_grid():
    """
    Generate grid for config panels.
    """
    grid = Gtk.Grid(
        row_spacing=6,
        column_spacing=6,
        column_homogeneous=False,
        margin_bottom=12,
    )
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
    context,
    grid,
    start_row,
    start_col=1,
    number=8,
    mode="all",
    key="facts-field",
    obj_type="Person",
):
    """
    Build facts field configuration section.
    """
    count = 1
    row = start_row
    while row < start_row + number:
        option = "{}.{}.{}-{}".format(space, context, key, count)
        user_select = FrameFieldSelector(
            option,
            grstate,
            count,
            mode=mode,
            dbid=True,
            obj_type=obj_type,
        )
        grid.attach(user_select, start_col, row, 2, 1)
        count = count + 1
        row = row + 1
    args = []
    if key != "attributes-field":
        if context in [
            "person",
            "child",
            "spouse",
            "parent",
            "sibling",
            "association",
            "participant",
            "people",
        ]:
            args = [
                (
                    "{}.{}.{}-skip-birth-alternates".format(
                        space, context, key
                    ),
                    _("Skip birth alternatives if birth found"),
                    _(
                        "If enabled then if a birth event was found other events considered to be birth alternatives such as baptism or christening will not be displayed."
                    ),
                ),
                (
                    "{}.{}.{}-skip-death-alternates".format(
                        space, context, key
                    ),
                    _("Skip death alternatives if death found"),
                    _(
                        "If enabled then if a death event was found other events considered to be death alternatives such as burial or cremation will not be displayed."
                    ),
                ),
            ]
        elif context == "family":
            args = [
                (
                    "{}.{}.{}-skip-marriage-alternates".format(
                        space, context, key
                    ),
                    _("Skip marriage alternatives if marriage found"),
                    _(
                        "If enabled then if a marriage event was found other events considered to be marriage alternatives such as marriage banns or license will not be displayed."
                    ),
                ),
                (
                    "{}.{}.{}-skip-divorce-alternates".format(
                        space, context, key
                    ),
                    _("Skip divorce alternatives if divorce found"),
                    _(
                        "If enabled then if a divorce event was found other events considered to be divorce alternatives such as divorce filing or annulment will not be displayed."
                    ),
                ),
            ]
    else:
        args = [
            (
                "{}.{}.{}-show-labels".format(space, context, key),
                _("Show attribute labels"),
                _(
                    "If enabled then the attribute and fact labels will be display."
                ),
            ),
        ]
    if args:
        for (option, label, tooltip) in args:
            configdialog.add_checkbox(
                grid,
                label,
                row,
                option,
                start=start_col,
                stop=start_col + 1,
                tooltip=tooltip,
            )
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
