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
from page_layout import LABELS

_ = glocale.translation.sgettext


class BaseProfilePage(Callback):
    """
    Provides functionality common to all object profile page views.
    """

    __signals__ = {
        'object-changed' : (str, str),
        'copy-to-clipboard' : (str, str),
    }

    def __init__(self, dbstate, uistate, config):
        Callback.__init__(self)
        self.dbstate = dbstate
        self.uistate = uistate
        self.config = config

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

    def render_group_view(self, obj_groups):
        """
        Identify group view type and call method to render it.
        """
        space = "preferences.profile.{}.layout".format(self.obj_type().lower())
        groups = self.config.get("{}.groups".format(space)).split(",")        
        if self.config.get("{}.tabbed".format(space)):
            return self.render_tabbed_group(obj_groups, space, groups)
        return self.render_untabbed_group(obj_groups, space, groups)
    
    def render_untabbed_group(self, obj_groups, space, groups):
        """
        Generate untabbed full page view for the groups.
        """
        gbox = None
        title = ""
        container = Gtk.HBox(spacing=3)
        for group in groups:
            if group not in obj_groups or not obj_groups[group]:
                continue
            if not self.config.get("{}.{}.visible".format(space, group)):
                continue
            if not gbox:
                gbox = Gtk.VBox(spacing=3)
            gbox.pack_start(obj_groups[group], expand=True, fill=True, padding=0)
            if not title:
                title = LABELS[group]
            else:
                title = "{} & {}".format(title, LABELS[group])
            if not self.config.get("{}.{}.stacked".format(space, group)):
                label = Gtk.Label(label=title)
                container.pack_start(gbox, expand=True, fill=True, padding=0)
                gbox = None
                title = ""
        return container

    def render_tabbed_group(self, obj_groups, space, groups):
        """
        Generate tabbed notebook view for the groups.
        """
        sbox = None
        title = ""
        in_stack = False
        container = Gtk.Notebook()
        for group in groups:
            if group not in obj_groups or not obj_groups[group]:
                continue
            if not self.config.get("{}.{}.visible".format(space, group)):
                continue
            gbox = Gtk.VBox(spacing=3)
            gbox.pack_start(obj_groups[group], expand=True, fill=True, padding=0)
            if not title:
                title = LABELS[group]
            else:
                title = "{} & {}".format(title, LABELS[group])
            if self.config.get("{}.{}.stacked".format(space, group)):
                in_stack = True
                if not sbox:
                    sbox = Gtk.HBox(spacing=3)
                sbox.pack_start(gbox, expand=True, fill=True, padding=0)
            else:
                if not in_stack:
                    obox = gbox
                else:
                    sbox.pack_start(gbox, expand=True, fill=True, padding=0)
                    obox = Gtk.VBox()
                    obox.add(sbox)
                    in_stack = False
            if not in_stack:
                label = Gtk.Label(label=title)
                container.append_page(obox, tab_label=label)
                sbox = None
                title = ""
        return container

    
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
                option, self.config, self.dbstate, self.uistate, count, dbid=True,
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
        reset = ConfigReset(configdialog, self.config, "{}.media".format(space), label=_("Reset Page Defaults"))
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
        reset = ConfigReset(configdialog, self.config, "{}.note".format(space), label=_("Reset Page Defaults"))
        grid.attach(reset, 1, 25, 1, 1)
        return _("Notes"), grid
    
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
