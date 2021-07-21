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
    TAG_DISPLAY_MODES,
    AttributeSelector,
    ConfigReset,
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

    def edit_active(self, *obj):
        """
        Edit the active page object.
        """
        if self.active_profile:
            self.active_profile.edit_object()

    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add a tag to the active page object.
        """
        if self.active_profile:
            if self.active_profile.obj.get_handle() == object_handle[1]:
                self.active_profile.obj.add_tag(tag_handle)
                commit_method = self.dbstate.db.method("commit_%s", self.active_profile.obj_type)
                commit_method(self.active_profile.obj, trans)

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
        key = "facts-field"
        if extra:
            key = "extra-field"
        while row < start_row + number:
            option = "{}.{}-{}".format(space, key, count)
            user_select = FrameFieldSelector(
                option, self.config, self.dbstate, self.uistate, count,
                dbid=True, defaults=self.defaults
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

    def _config_metadata_attributes(self, grid, space, start_row, start_col=1, number=8, obj_type="Person"):
        """
        Build metadata display field configuration section.
        """
        count = 1
        row = start_row
        while row < start_row + number:
            option = "{}.metadata-attribute-{}".format(space, count)
            attr_select = AttributeSelector(
                option, self.config, self.dbstate.db, obj_type, dbid=True,
                tooltip=_("This option allows you to select the name of an attribute. The value of the attribute, if one is found, will then be displayed in the metadata section of the frame beneath the Gramps Id.")
            )
            label = Gtk.Label(
                halign=Gtk.Align.START, label="{} {}: ".format(_("Field"), count)
            )
            grid.attach(label, start_col, row, 1, 1)
            grid.attach(attr_select, start_col + 1, row, 1, 1)
            count = count + 1
            row = row + 1

    def _media_panel(self, configdialog, space):
        """
        Builds media options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "{}.media.tag-format".format(space),
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "{}.media.tag-width".format(space),
            (1, 20),
        )
        configdialog.add_checkbox(
            grid, _("Sort media by date"),
            4, "{}.media.sort-by-date".format(space),
            tooltip=_("Enabling this option will sort the media by date.")
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show date"),
            10, "{}.media.show-date".format(space),
            tooltip=_("Enabling this option will show the media date if it is available.")
        )
        configdialog.add_text(grid, _("Metadata Display Fields"), 15, start=1, bold=True)
        self._config_metadata_attributes(grid, "{}.media".format(space), 16, start_col=1, number=4, obj_type="Media")
        reset = ConfigReset(configdialog, self.config, "{}.media".format(space), defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Media"), grid

    def _notes_panel(self, configdialog, space):
        """
        Builds note options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "{}.note.tag-format".format(space),
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "{}.note.tag-width".format(space),
            (1, 20),
        )
        reset = ConfigReset(configdialog, self.config, "{}.note".format(space), defaults=self.defaults, label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Notes"), grid
    
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
