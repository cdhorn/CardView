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
Base Profile Page
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk, Gdk


# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.callback import Callback
from gramps.gui.widgets import BasicLabel


# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from frame_utils import (
    AttributeSelector,
    FrameFieldSelector
)

_ = glocale.translation.sgettext


class BaseProfilePage(Callback):
    """
    Provides functionality common to all object profile page views.
    """

    __signals__ = {
        'object-changed' : (str, str),
        'copy-to-clipboard' : (str, str),
    }

    def __init__(self, dbstate, uistate, config, defaults):
        Callback.__init__(self)
        self.dbstate = dbstate
        self.uistate = uistate
        self.config = config
        self.defaults = defaults

    def callback_router(self, signal, payload):
        """
        Emit signal on behalf of a managed object.
        """
        self.emit(signal, payload)

    def create_grid(self):
        """
        Generate grid for config panels.
        """
        grid = Gtk.Grid(row_spacing=6, column_spacing=6, column_homogeneous=False)
        grid.set_border_width(12)
        return grid

    def _config_facts_fields(self, configdialog, grid, space, start_row, start_col=1, number=8, extra=False):
        """
        Build facts field configuration section.
        """
        count = 1
        row = start_row
        text = _("Facts field")
        key = "facts-field"
        if extra:
            text = _("Extra field")
            key = "extra-field"
        while row < start_row + number:
            option = "{}.{}-{}".format(space, key, count)
            user_select = FrameFieldSelector(
                option, self.config, self.dbstate, self.uistate, count,
                dbid=True, defaults=self.defaults, text=text
            )
            grid.attach(user_select, start_col, row, 2, 1)
            count = count + 1
            row = row + 1
        option = "{}.{}-skip-birth-alternates".format(space, key)
        configdialog.add_checkbox(
            grid, _("Skip birth alternatives if birth found"),
            row, option, start=start_col, stop=start_col+1,
            tooltip=_("If enabled then if a birth event was found other events considered to be birth alternatives such as baptism or christening will not be displayed.")
        )
        row = row + 1
        option = "{}.{}-skip-death-alternates".format(space, key)
        configdialog.add_checkbox(
            grid, _("Skip death alternates if death found"),
            row, option, start=start_col, stop=start_col+1,
            tooltip=_("If enabled then if a death event was found other events considered to be death alternatives such as burial or cremation will not be displayed.")
        )
        row = row + 1

    def _config_metadata_attributes(self, grid, space, start_row, start_col=1, number=8):
        """
        Build metadata custom attribute configuration section.
        """
        count = 1
        row = start_row
        while row < start_row + number:
            option = "{}.metadata-attribute-{}".format(space, count)
            attr_select = AttributeSelector(
                option, self.config, self.dbstate.db, "Person", dbid=True,
                tooltip=_("This option allows you to select the name of a custom user defined attribute about the person. The value of the attribute, if one is found, will then be displayed in the metadata section of the user frame beneath the Gramps Id.")
            )
            label = Gtk.Label(
                halign=Gtk.Align.START, label="{} {}: ".format(_("Metadata attribute"), count)
            )
            grid.attach(label, start_col, row, 1, 1)
            grid.attach(attr_select, start_col + 1, row, 1, 1)
            count = count + 1
            row = row + 1
    
    def add_color(self, grid, label, index, constant, col=0):
        """
        Add color chooser widget with label and hex value to the grid.
        """
        lwidget = BasicLabel(_("%s: ") % label)
        colors = self.config.get(constant)
        if isinstance(colors, list):
            scheme = global_config.get('colors.scheme')
            hexval = colors[scheme]
        else:
            hexval = colors
        color = Gdk.color_parse(hexval)
        entry = Gtk.ColorButton(color=color)
        color_hex_label = BasicLabel(hexval)
        color_hex_label.set_hexpand(True)
        entry.connect('notify::color', self.update_color, constant,
                      color_hex_label)
        grid.attach(lwidget, col, index, 1, 1)
        grid.attach(entry, col+1, index, 1, 1)
        grid.attach(color_hex_label, col+2, index, 1, 1)
        return entry

    def update_color(self, obj, pspec, constant, color_hex_label):
        """
        Called on changing some color.
        Either on programmatically color change.
        """
        rgba = obj.get_rgba()
        hexval = "#%02x%02x%02x" % (int(rgba.red * 255),
                                    int(rgba.green * 255),
                                    int(rgba.blue * 255))
        color_hex_label.set_text(hexval)
        colors = self.config.get(constant)
        if isinstance(colors, list):
            scheme = global_config.get('colors.scheme')
            colors[scheme] = hexval
            self.config.set(constant, colors)
        else:
            self.config.set(constant, hexval)
