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
from ..common.common_utils import ConfigReset, make_scrollable
from ..frames.frame_selectors import FrameFieldSelector

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
        hexpand=False,
        vexpand=False,
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
    return make_scrollable(vbox, hexpand=True)


def config_facts_fields(
    configdialog,
    grstate,
    space,
    context,
    grid,
    start_row,
    start_col=1,
    number=10,
    mode="all",
    key="lfield",
    obj_type="Person",
):
    """
    Build facts field configuration section.
    """
    size_groups = {
        "label": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        "type": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
    }
    count = 1
    row = start_row
    prefix = "".join((space, ".", context, ".", key, "-"))
    while row < start_row + number:
        option = "".join((prefix, str(count)))
        user_select = FrameFieldSelector(
            option,
            grstate,
            count,
            mode=mode,
            dbid=True,
            obj_type=obj_type,
            size_groups=size_groups,
        )
        grid.attach(user_select, start_col, row, 2, 1)
        count = count + 1
        row = row + 1
    args = []
    if key != "rfield":
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
                    "".join((prefix, "skip-birth-alternates")),
                    _("Skip birth alternatives if birth found"),
                    _(
                        "If enabled then if a birth event was found other "
                        "events considered to be birth alternatives such "
                        "as baptism or christening will not be displayed."
                    ),
                ),
                (
                    "".join((prefix, "skip-death-alternates")),
                    _("Skip death alternatives if death found"),
                    _(
                        "If enabled then if a death event was found other "
                        "events considered to be death alternatives such as "
                        "burial or cremation will not be displayed."
                    ),
                ),
            ]
        elif context == "family":
            args = [
                (
                    "".join((prefix, "skip-marriage-alternates")),
                    _("Skip marriage alternatives if marriage found"),
                    _(
                        "If enabled then if a marriage event was found other "
                        "events considered to be marriage alternatives such "
                        "as marriage banns or license will not be displayed."
                    ),
                ),
                (
                    "".join((prefix, "skip-divorce-alternates")),
                    _("Skip divorce alternatives if divorce found"),
                    _(
                        "If enabled then if a divorce event was found other "
                        "events considered to be divorce alternatives such "
                        "as divorce filing or annulment will not be displayed."
                    ),
                ),
            ]
    else:
        args = [
            (
                "".join((prefix, "show-labels")),
                _("Show attribute labels"),
                _(
                    "If enabled then both the attribute name and value will "
                    "be displayed."
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
