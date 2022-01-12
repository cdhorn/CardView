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
Color scheme configuration dialog functions
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.widgets import BasicLabel

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .config_utils import ConfigPreferences, add_config_reset, create_grid

_ = glocale.translation.sgettext


BOLD_MARKUP = "<b>{}</b>"

CONFIDENCE_TYPE = (
    "Confidence",
    _("Confidence color scheme"),
    "colors.confidence",
)


CONFIDENCE_OPTIONS = [
    (_("Background for Very High"), "very-high", 1, 1),
    (_("Background for High"), "high", 2, 1),
    (_("Background for Normal"), "normal", 3, 1),
    (_("Background for Low"), "low", 4, 1),
    (_("Background for Very Low"), "very-low", 5, 1),
    (_("Border for Very High"), "border-very-high", 1, 4),
    (_("Border for High"), "border-high", 2, 4),
    (_("Border for Normal"), "border-normal", 3, 4),
    (_("Border for Low"), "border-low", 4, 4),
    (_("Border for Very Low"), "border-very-low", 5, 4),
]

RELATION_TYPE = (
    "Relation",
    _("Relationship color scheme"),
    "colors.relations",
)

RELATION_OPTIONS = [
    (_("Background for Active Person"), "active", 1, 1),
    (_("Background for Spouse"), "spouse", 2, 1),
    (_("Background for Father"), "father", 3, 1),
    (_("Background for Mother"), "mother", 4, 1),
    (_("Background for Brother"), "brother", 5, 1),
    (_("Background for Sister"), "sister", 6, 1),
    (_("Background for Son"), "son", 7, 1),
    (_("Background for Daughter"), "daughter", 8, 1),
    (_("Background for None"), "none", 9, 1),
    (_("Border for Active Person"), "border-active", 1, 4),
    (_("Border for Spouse"), "border-spouse", 2, 4),
    (_("Border for Father"), "border-father", 3, 4),
    (_("Border for Mother"), "border-mother", 4, 4),
    (_("Border for Brother"), "border-brother", 5, 4),
    (_("Border for Sister"), "border-sister", 6, 4),
    (_("Border for Son"), "border-son", 7, 4),
    (_("Border for Daughter"), "border-daughter", 8, 4),
    (_("Border for None"), "border-none", 9, 4),
]

EVENT_TYPE = (
    "Event",
    _("Event category color scheme"),
    "colors.events",
)

EVENT_OPTIONS = [
    (_("Background for Vital Events"), "vital", 1, 1),
    (_("Background for Family Events"), "family", 2, 1),
    (_("Background for Religious Events"), "religious", 3, 1),
    (_("Background for Vocational Events"), "vocational", 4, 1),
    (_("Background for Academic Events"), "academic", 5, 1),
    (_("Background for Travel Events"), "travel", 6, 1),
    (_("Background for Legal Events"), "legal", 7, 1),
    (_("Background for Residence Events"), "residence", 8, 1),
    (_("Background for Other Events"), "other", 9, 1),
    (_("Background for Custom Events"), "custom", 10, 1),
    (_("Border for Vital Events"), "border-vital", 1, 4),
    (_("Border for Family Events"), "border-family", 2, 4),
    (_("Border for Religious Events"), "border-religious", 3, 4),
    (_("Border for Vocational Events"), "border-vocational", 4, 4),
    (_("Border for Academic Events"), "border-academic", 5, 4),
    (_("Border for Travel Events"), "border-travel", 6, 4),
    (_("Border for Legal Events"), "border-legal", 7, 4),
    (_("Border for Residence Events"), "border-residence", 8, 4),
    (_("Border for Other Events"), "border-other", 9, 4),
    (_("Border for Custom Events"), "border-custom", 10, 4),
]

ROLE_TYPE = (
    "Role",
    _("Event role color scheme"),
    "colors.roles",
)

ROLE_OPTIONS = [
    (_("Background for Primary Role"), "primary", 1, 1),
    (_("Background for Secondary Role"), "secondary", 2, 1),
    (_("Background for Family Role"), "family", 3, 1),
    (_("Background for Implicit Family Role"), "implicit", 4, 1),
    (_("Background for Unknown Role"), "unknown", 5, 1),
    (_("Border for Primary Role"), "border-primary", 1, 4),
    (_("Border for Secondary Role"), "border-secondary", 2, 4),
    (_("Border for Family Role"), "border-family", 3, 4),
    (_("Border for Implicit Family Role"), "border-implicit", 4, 4),
    (_("Border for Unknown Role"), "border-unknown", 5, 4),
]


def build_color_grid(configdialog, grstate, scheme_type, scheme_options):
    """
    Build color scheme selection grid for the configuration dialog.
    """
    grid = create_grid()
    configdialog.add_text(
        grid,
        _(
            "The default Gramps color scheme is managed under "
            "the Gramps preferences"
        ),
        0,
        start=0,
        bold=True,
    )
    preferences = ConfigPreferences(grstate)
    grid.attach(preferences, 0, 1, 1, 1)
    scroll_window = Gtk.ScrolledWindow()
    colors_grid = create_grid()
    scroll_window.add(colors_grid)
    scroll_window.set_vexpand(True)
    scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    grid.attach(scroll_window, 0, 3, 7, 1)
    key, title, space = scheme_type
    label = Gtk.Label(halign=Gtk.Align.START, margin_top=12)
    label.set_markup(BOLD_MARKUP.format(title))
    colors_grid.attach(label, 0, 0, 2, 1)

    light_grid = create_grid()
    label = Gtk.Label(halign=Gtk.Align.START, margin_top=12)
    label.set_markup(BOLD_MARKUP.format(_("Light colors")))
    light_grid.attach(label, 0, 0, 2, 1)
    dark_grid = create_grid()
    label = Gtk.Label(halign=Gtk.Align.START, margin_top=12)
    label.set_markup(BOLD_MARKUP.format(_("Dark colors")))
    dark_grid.attach(label, 0, 0, 2, 1)

    for label, key, row, column in scheme_options:
        option = "{}.{}".format(space, key)
        add_color(grstate.config, light_grid, label, option, (row, column), 0)
        add_color(grstate.config, dark_grid, label, option, (row, column), 1)
    colors_grid.attach(light_grid, 0, 1, 2, 1)
    colors_grid.attach(dark_grid, 0, 2, 2, 1)
    return add_config_reset(configdialog, grstate, space, grid)


def add_color(config, grid, text, option, coordinates, scheme):
    """
    Add color chooser widget with label and hex value to the grid.
    """
    row, column = coordinates
    label = BasicLabel(text)
    colors = config.get(option)
    if isinstance(colors, list):
        hexval = colors[scheme]
    else:
        hexval = colors
    color = Gdk.color_parse(hexval)
    entry = Gtk.ColorButton(color=color)
    color_hex_label = BasicLabel(hexval)
    color_hex_label.set_hexpand(True)
    entry.connect(
        "notify::color", update_color, config, option, color_hex_label, scheme
    )
    grid.attach(label, column, row, 1, 1)
    grid.attach(entry, column + 1, row, 1, 1)
    grid.attach(color_hex_label, column + 2, row, 1, 1)
    return entry


def update_color(obj, _dummy_obj, config, option, color_hex_label, scheme):
    """
    Called on changing some color.
    Either on programmatically color change.
    """
    rgba = obj.get_rgba()
    hexval = "#%02x%02x%02x" % (
        int(rgba.red * 255),
        int(rgba.green * 255),
        int(rgba.blue * 255),
    )
    color_hex_label.set_text(hexval)
    colors = config.get(option)
    if isinstance(colors, list):
        colors[scheme] = hexval
        config.set(option, colors)
    else:
        config.set(option, hexval)
