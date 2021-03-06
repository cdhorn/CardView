#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
# Copyright (C) 2021-2022  Christopher Horn
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
Config utility classes and functions
"""

# -------------------------------------------------------------------------
#
# GTK Modules
#
# -------------------------------------------------------------------------
from gi.repository import GObject, Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.configure import GrampsPreferences
from gramps.gui.display import display_url

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_utils import make_scrollable
from .config_selectors import CardFieldSelector

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# ConfigPreferences Class
#
# -------------------------------------------------------------------------
class ConfigPreferences(Gtk.ButtonBox):
    """
    Class to launch Gramps default preferences.
    """

    def __init__(self, grstate):
        Gtk.ButtonBox.__init__(self, spacing=6)
        self.set_layout(Gtk.ButtonBoxStyle.START)
        self.button = Gtk.Button(hexpand=False)
        self.pack_start(self.button, False, False, 0)
        self.grstate = grstate
        self.button.set_label(_("Preferences"))
        self.button.connect("clicked", self.open_preferences)
        self.button.set_tooltip_text(
            _(
                "This option will launch the Gramps default preferences "
                "dialog."
            )
        )

    def open_preferences(self, _dummy_obj):
        """
        Open the preferences dialog.
        """
        try:
            GrampsPreferences(self.grstate.uistate, self.grstate.dbstate)
        except WindowActiveError:
            return


# -------------------------------------------------------------------------
#
# ConfigReset Class
#
# -------------------------------------------------------------------------
class ConfigReset(Gtk.ButtonBox):
    """
    Class to manage resetting configuration options.
    """

    def __init__(self, dialog, grstate, space, label=None):
        Gtk.ButtonBox.__init__(self, spacing=6)
        self.set_layout(Gtk.ButtonBoxStyle.END)
        self.button = Gtk.Button(hexpand=False)
        self.pack_start(self.button, False, False, 0)
        self.grstate = grstate
        self.dialog = dialog
        self.config = grstate.config
        self.space = space
        if label:
            self.button.set_label(label)
        else:
            self.button.set_label(_("Defaults"))
        self.button.connect("clicked", self.reset_option_space)
        self.button.set_tooltip_text(
            _(
                "This option will examine a set of options and set any "
                "that were changed back to their default value. It may "
                "apply to a whole page or in some cases a part of a page. "
                "Note if it finds and has to reset any values when done "
                "it will close the configuration dialog and you will need "
                "to reopen it. Redraw logic has not been implemented yet."
            )
        )

    def confirm_reset(self):
        """
        Confirm reset action.
        """
        dialog = Gtk.Dialog(parent=self.grstate.uistate.window)
        dialog.set_title(_("Reset Option Defaults"))
        dialog.set_default_size(500, 300)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)

        message = _(
            "You are about to reset the options on this page back to "
            "their default values.\n\n"
            "If any options are found to reset then when done the "
            "configuration dialog will close and you will need to "
            "reopen it if needed.\n\n"
            "Are you sure you want to proceed?"
        )
        label = Gtk.Label(
            hexpand=True,
            vexpand=True,
            halign=Gtk.Align.CENTER,
            justify=Gtk.Justification.CENTER,
            use_markup=True,
            wrap=True,
            label=message,
        )
        dialog.vbox.add(label)
        all_button = Gtk.CheckButton(
            label=_("Reset all options to defaults, not just this page.")
        )
        dialog.vbox.add(all_button)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            if all_button.get_active():
                self.space = "all"
            return True
        return False

    def reset_option_space(self, _dummy_obj):
        """
        Reset any options that changed in a given space.
        """
        if not self.confirm_reset():
            return
        if self.space == "all":
            self.config.reset()
            self.config.save()
            self.dialog.done(None, None)
            return
        reset_option = False
        options = self.get_option_space()
        for option in options:
            current_value = self.config.get(option)
            if self.config.has_default(option):
                default_value = self.config.get_default(option)
                if current_value != default_value:
                    self.config.set(option, default_value)
                    reset_option = True
        if reset_option:
            self.config.save()
            self.dialog.done(None, None)
        return

    def get_option_space(self):
        """
        Get all the options available in a given space.
        """
        if "." in self.space:
            section = self.space.split(".")[0]
            prefix = self.space.replace("%s." % section, "")
        else:
            section = self.space
            prefix = ""
        settings = self.config.get_section_settings(section)
        prefix_length = len(prefix)
        options = []
        for setting in settings:
            if setting[:prefix_length] == prefix:
                options.append("%s.%s" % (section, setting))
        return options


# -------------------------------------------------------------------------
#
# TemplateCommentsEntry Class
#
# -------------------------------------------------------------------------
class TemplateCommentsEntry(Gtk.VBox):
    """
    Simple text view for user to edit template comments section.
    """

    def __init__(self, grstate, option):
        Gtk.HBox.__init__(self, hexpand=True, spacing=6)
        self.grstate = grstate
        self.option = option
        self.defer_refresh = False
        self.defer_refresh_id = None
        self.text_buffer = Gtk.TextBuffer()
        text = grstate.config.get(option)
        self.text_buffer.set_text("\n".join(tuple(text)))
        self.text_buffer.connect("changed", self.__defer_save)
        text_view = Gtk.TextView(buffer=self.text_buffer)
        text_view.set_margin_start(6)
        text_view.set_margin_end(6)
        text_view.set_margin_top(6)
        text_view.set_margin_bottom(6)
        frame = Gtk.Frame()
        css = ".frame { border: solid; border-radius: 5px; border: 1px; }".encode(
            "utf-8"
        )
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
        box = Gtk.Box(spacing=6)
        box.add(text_view)
        frame.add(box)
        self.pack_start(frame, True, True, 0)

    def __defer_save(self, *_dummy_args):
        """
        Defer save a short bit in case user still typing.
        """
        if not self.defer_refresh_id:
            self.defer_refresh_id = GObject.timeout_add(
                1000, self.__perform_save
            )
        else:
            self.defer_refresh = True

    def __perform_save(self):
        """
        Perform the save.
        """
        if self.defer_refresh:
            self.defer_refresh = False
            return True
        self.defer_refresh = False
        lines = self.text_buffer.get_text(
            self.text_buffer.get_start_iter(),
            self.text_buffer.get_end_iter(),
            False,
        )
        line_list = lines.split("\n")
        self.grstate.config.set(self.option, line_list)
        GObject.source_remove(self.defer_refresh_id)
        self.defer_refresh_id = None
        return False


# -------------------------------------------------------------------------
#
# HelpButton Class
#
# -------------------------------------------------------------------------
class HelpButton(Gtk.Button):
    """
    Simple help button
    """

    def __init__(self, url):
        Gtk.Button.__init__(self)
        self.url = url
        self.set_label(_("Help"))
        self.connect("clicked", self.launch_help)

    def launch_help(self, *_dummy_args):
        """
        Lauch help
        """
        display_url(self.url)


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


def add_config_buttons(configdialog, grstate, space, grid, url):
    """
    Add help and configuration reset buttons.
    """
    vbox = Gtk.VBox(margin=12)
    vbox.pack_start(grid, True, True, 0)
    hbox = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
    hbox.add(HelpButton(url))
    hbox.add(ConfigReset(configdialog, grstate, space))
    vbox.pack_end(hbox, False, False, 0)
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
        user_select = CardFieldSelector(
            option,
            grstate,
            count,
            mode=mode,
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


def config_event_fields(grstate, key="alert", count=12):
    """
    Build event status fields configuration section.
    """
    grid = create_grid()
    half = int(count / 2)
    grid1 = config_event_grid(grstate, key, start=1, count=half)
    grid2 = config_event_grid(grstate, key, start=(half + 1), count=half)
    grid.attach(grid1, 1, 0, 1, 1)
    grid.attach(grid2, 2, 0, 1, 1)
    return grid


def config_event_grid(grstate, key, start=1, count=6):
    """
    Build event entry grid.
    """
    grid = create_grid()
    size_groups = {
        "label": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        "type": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
    }
    prefix = "".join(("status.", key, "-"))
    row_start = start
    row_end = start + count
    for row in range(row_start, row_end):
        option = "".join((prefix, str(row)))
        user_select = CardFieldSelector(
            option,
            grstate,
            row,
            mode="status",
            obj_type="Person",
            size_groups=size_groups,
        )
        grid.attach(user_select, 1, row, 2, 1)
    return grid


def get_event_fields(grstate, key, count=12):
    """
    Return list of events from event fields.
    """
    events = []
    prefix = "".join(("status.", key, "-"))
    for number in range(1, count):
        option = "".join((prefix, str(number)))
        value = grstate.config.get(option).split(":")
        if len(value) > 1:
            events.append(value[1])
    return events
