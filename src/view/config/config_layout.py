#
# Gramps - a GTK+/GNOME based genealogy program
#
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
Page layout configuration dialog
"""

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.ddtargets import DdTargets

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_const import GROUP_LABELS
from ..common.common_utils import make_scrollable, set_dnd_css
from .config_const import PAGES, HELP_CONFIG_PAGE_LAYOUT
from .config_utils import ConfigReset, create_grid, HelpButton

_ = glocale.translation.sgettext


GROUPS = "{}.groups"
TABBED = "{}.tabbed"
SCROLLED = "{}.scrolled"
VISIBLE = "{}.visible"
APPEND = "{}.append"


def build_layout_grid(configdialog, grstate, page_type=None, *_dummy_args):
    """
    Build and return layout grid.
    """
    grid = create_grid()
    if page_type:
        for page in PAGES:
            if page[0] == page_type:
                page_lang = page[1]
                break
        tab = (page_type, page_lang)
        vbox = Gtk.VBox(spacing=3)
        vbox.pack_start(
            ProfilePageLayout(configdialog, grstate, tab), False, False, 0
        )
        grid.add(vbox)
    else:
        notebook = Gtk.Notebook(vexpand=True, hexpand=True)
        notebook.set_tab_pos(Gtk.PositionType.LEFT)
        for tab in PAGES:
            page = ProfilePageLayout(configdialog, grstate, tab)
            label = Gtk.Label(label=tab[1])
            notebook.append_page(
                make_scrollable(page, hexpand=True), tab_label=label
            )
        grid.add(notebook)
    return grid


# ------------------------------------------------------------------------
#
# ProfilePageLayout Class
#
# ------------------------------------------------------------------------
class ProfilePageLayout(Gtk.VBox):
    """
    Class to handle layout for a specific page.
    """

    def __init__(self, configdialog, grstate, tab):
        Gtk.VBox.__init__(self, spacing=6, margin=12)
        self.configdialog = configdialog
        self.grstate = grstate
        self.config = grstate.config
        self.obj_type, self.obj_type_lang = tab
        self.space = "layout.{}".format(self.obj_type.lower())
        self.revert = []
        self.draw()

    def draw(self):
        """
        Render options content.
        """
        list(map(self.remove, self.get_children()))
        groups = {
            "label": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "visible": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "append": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        option = TABBED.format(self.space)
        self.tabbed = Gtk.CheckButton(label=_("Tabbed Mode"))
        self.tabbed.set_active(self.config.get(option))
        self.tabbed.connect("clicked", self.toggle_mode)
        self.pack_start(self.tabbed, False, False, 6)
        option = SCROLLED.format(self.space)
        self.scrolled = Gtk.CheckButton(label=_("Scrolled Mode"))
        self.scrolled.set_active(self.config.get(option))
        self.pack_start(self.scrolled, False, False, 6)

        self.columns = ProfileColumnLayout()
        current_groups = self.config.get(GROUPS.format(self.space))
        current_groups = self.get_valid_layout_groups(
            self.obj_type, current_groups.split(",")
        )

        number = 0
        for field in current_groups:
            space = "{}.{}".format(self.space, field)
            row = ProfileRowLayout(
                self.config, space, GROUP_LABELS[field], groups, number
            )
            self.columns.add_row(row)
            number = number + 1
        self.pack_start(self.columns, False, False, 6)

        box = Gtk.HBox()
        bbox = Gtk.ButtonBox(spacing=6)
        bbox.set_layout(Gtk.ButtonBoxStyle.START)
        bbox.pack_start(HelpButton(HELP_CONFIG_PAGE_LAYOUT), False, False, 0)
        apply = Gtk.Button(label=_("Apply"))
        apply.connect("clicked", self.apply_changes)
        bbox.pack_start(apply, False, False, 0)
        self.undo = Gtk.Button(label=_("Undo"))
        self.undo.connect("show", self.undo_hide)
        self.undo.connect("clicked", self.undo_changes)
        bbox.pack_start(self.undo, False, False, 0)
        box.pack_start(bbox, False, False, 0)
        defaults = ConfigReset(self.configdialog, self.grstate, self.space)
        box.pack_end(defaults, False, False, 0)
        self.pack_end(box, False, False, 0)
        self.show_all()

    def get_valid_layout_groups(self, obj_type, current_groups):
        """
        Examine options and construct list of valid groups for an object view.
        """
        valid_groups = []
        available_groups = self.get_all_layout_groups(obj_type)
        for group in current_groups:
            if group in available_groups:
                valid_groups.append(group)
        for group in available_groups:
            if group not in valid_groups:
                valid_groups.append(group)
        return valid_groups

    def get_all_layout_groups(self, obj_type):
        """
        Extract all available groups for an object view.
        """
        settings = self.config.get_section_settings("layout")
        prefix = obj_type.lower()
        prefix_length = len(prefix)
        groups = []
        for setting in settings:
            if setting[:prefix_length] == prefix and "visible" in setting:
                groups.append(setting.split(".")[1])
        return groups

    def apply_changes(self, *_dummy_obj):
        """
        Apply changes if any found.
        """
        self.revert = []
        option = TABBED.format(self.space)
        if self.config.get(option) != self.tabbed.get_active():
            self.revert.append((option, self.config.get(option)))
            self.config.set(option, self.tabbed.get_active())
        option = SCROLLED.format(self.space)
        if self.config.get(option) != self.scrolled.get_active():
            self.revert.append((option, self.config.get(option)))
            self.config.set(option, self.scrolled.get_active())

        columns = []
        for row in self.columns.rows:
            columns.append(row.space.split(".")[-1])
            option = VISIBLE.format(row.space)
            if self.config.get(option) != row.visible.get_active():
                self.revert.append((option, self.config.get(option)))
                self.config.set(option, row.visible.get_active())
            option = APPEND.format(row.space)
            if self.config.get(option) != row.append.get_active():
                self.revert.append((option, self.config.get(option)))
                self.config.set(option, row.append.get_active())

        option = GROUPS.format(self.space)
        if self.config.get(option) != ",".join(columns):
            self.revert.append((option, self.config.get(option)))
            self.config.set(option, ",".join(columns))
        if self.revert:
            self.config.save()
            self.undo.set_visible(True)
        self.draw()
        self.grstate.reload_config(refresh_only=False, defer_refresh=False)

    def apply_defaults(self, *_dummy_obj):
        """
        Apply defaults if any changes found.
        """
        self.revert = []
        option = TABBED.format(self.space)
        if self.config.get_default(option) != self.tabbed.get_active():
            self.revert.append((option, self.tabbed.get_active()))
            self.config.set(option, self.config.get_default(option))
        option = SCROLLED.format(self.space)
        if self.config.get_default(option) != self.scrolled.get_active():
            self.revert.append((option, self.scrolled.get_active()))
            self.config.set(option, self.config.get_default(option))

        columns = []
        for row in self.columns.rows:
            columns.append(row.space.split(".")[-1])
            option = VISIBLE.format(row.space)
            if self.config.get_default(option) != row.visible.get_active():
                self.revert.append((option, row.visible.get_active()))
                self.config.set(option, self.config.get_default(option))
            option = APPEND.format(row.space)
            if self.config.get_default(option) != row.append.get_active():
                self.revert.append((option, row.append.get_active()))
                self.config.set(option, self.config.get_default(option))

        option = GROUPS.format(self.space)
        if self.config.get_default(option) != ",".join(columns):
            self.revert.append((option, ",".join(columns)))
            self.config.set(option, self.config.get_default(option))
        if self.revert:
            self.config.save()
        self.draw()

    def undo_hide(self, *_dummy_obj):
        """
        Hide button if nothing available to undo.
        """
        if not self.revert:
            self.undo.set_visible(False)

    def undo_changes(self, *_dummy_obj):
        """
        Undo the last set of changes.
        """
        if self.revert:
            for option, value in self.revert:
                self.config.set(option, value)
            self.config.save()
            self.revert = []
            self.draw()

    def toggle_mode(self, *_dummy_obj):
        """
        Toggle option visibility based on mode.
        """
        self.tabbed.set_inconsistent(False)


# ------------------------------------------------------------------------
#
# ProfileColumnLayout Class
#
# ------------------------------------------------------------------------
class ProfileColumnLayout(Gtk.ListBox):
    """
    Class to manage order of columns on page.
    """

    def __init__(self):
        Gtk.ListBox.__init__(self, hexpand=False)
        self.set_sort_func(None)
        self.dnd_type = None
        self.dnd_icon = "x-office-document"
        self.rows = []
        self.row_previous = 0
        self.row_current = 0
        self.row_previous_provider = None
        self.row_current_provider = None
        self.drag_dest_set(
            Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
            [DdTargets.TEXT.target()],
            Gdk.DragAction.MOVE,
        )
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-motion", self.on_drag_motion)
        self.connect("drag-leave", self.on_drag_leave)

    def add_row(self, card):
        """
        Add a card row object.
        """
        self.rows.append(card)
        row = Gtk.ListBoxRow(selectable=False)
        row.add(self.rows[-1])
        self.add(row)

    def on_drag_data_received(
        self,
        _dummy_widget,
        _dummy_drag_context,
        _dummy_x,
        _dummy_y,
        data,
        _dummy_info,
        _dummy_time,
    ):
        """
        Extract the data and handle any required actions.
        """
        self.reset_dnd_css()
        if data and data.get_text():
            source_number = data.get_text()
            source_index = 0
            for card in self.rows:
                if str(card.number) == source_number:
                    if self.row_current == source_index:
                        break
                    row_moving = self.get_row_at_index(source_index)
                    card_moving = self.rows[source_index]
                    self.remove(row_moving)
                    self.rows.remove(card_moving)
                    if self.row_current < source_index:
                        self.insert(row_moving, self.row_current)
                        self.rows.insert(self.row_current, card_moving)
                        break
                    if self.row_current == self.row_previous:
                        self.add(row_moving)
                        self.rows.append(card_moving)
                        break
                    self.insert(row_moving, self.row_current - 1)
                    self.rows.insert(self.row_current - 1, card_moving)
                    break
                source_index = source_index + 1
        self.row_previous = 0
        self.row_current = 0

    def on_drag_motion(
        self, _dummy_widget, _dummy_context, _dummy_x, y_location, _dummy_time
    ):
        """
        Update the view while a user drag and drop is underway.
        """
        self.reset_dnd_css()
        current_row = self.get_row_at_y(y_location)
        if current_row:
            allocation = current_row.get_allocation()
            if allocation:
                self.update_rows_for_drag_motion(
                    y_location, current_row, allocation
                )

    def update_rows_for_drag_motion(self, y_location, current_row, allocation):
        """
        Update row state as needed.
        """
        if y_location < allocation.y + allocation.height / 2:
            self.row_current = current_row.get_index()
            self.row_previous = self.row_current - 1
            self.row_previous = max(self.row_previous, 0)
        else:
            self.row_previous = current_row.get_index()
            self.row_current = self.row_previous + 1
            if self.row_current >= len(self) - 1:
                self.row_current = len(self) - 1

        if self.row_current == 0 and self.row_previous == 0:
            self.row_current_provider = set_dnd_css(
                self.rows[self.row_current], top=True
            )
        elif self.row_current == self.row_previous:
            self.row_current_provider = set_dnd_css(
                self.rows[self.row_current], top=False
            )
        elif self.row_current > self.row_previous:
            self.row_previous_provider = set_dnd_css(
                self.rows[self.row_previous], top=False
            )
            self.row_current_provider = set_dnd_css(
                self.rows[self.row_current], top=True
            )
        else:
            self.row_previous_provider = set_dnd_css(
                self.rows[self.row_previous], top=True
            )
            self.row_current_provider = set_dnd_css(
                self.rows[self.row_current], top=False
            )

    def on_drag_leave(self, *_dummy_obj):
        """
        Reset custom CSS if drag no longer in focus.
        """
        self.reset_dnd_css()

    def reset_dnd_css(self):
        """
        Reset custom CSS for the drag and drop view.
        """
        if self.row_previous_provider:
            context = self.rows[self.row_previous].get_style_context()
            context.remove_provider(self.row_previous_provider)
            self.row_previous_provider = None
        self.rows[self.row_previous].set_css_style()
        if self.row_current_provider:
            context = self.rows[self.row_current].get_style_context()
            context.remove_provider(self.row_current_provider)
            self.row_current_provider = None
        self.rows[self.row_current].set_css_style()


# ------------------------------------------------------------------------
#
# ProfileRowLayout Class
#
# ------------------------------------------------------------------------
class ProfileRowLayout(Gtk.Frame):
    """
    Class to manage object group specific options.
    """

    def __init__(self, config, space, name, groups, number):
        Gtk.Frame.__init__(self, expand=False)
        self.config = config
        self.space = space
        self.number = number

        hbox = Gtk.HBox(hexpand=False, halign=Gtk.Align.START, spacing=6)
        ebox = Gtk.EventBox()
        ebox.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.MOVE
        )
        target = Gtk.TargetList.new([])
        target.add(
            DdTargets.TEXT.atom_drag_type,
            DdTargets.TEXT.target_flags,
            DdTargets.TEXT.app_id,
        )
        ebox.drag_source_set_target_list(target)
        ebox.drag_source_set_icon_name("x-office-document")
        ebox.connect("drag_data_get", self.drag_data_get)
        ebox.add(hbox)
        self.add(ebox)

        label = Gtk.Label(
            label=name, halign=Gtk.Align.START, justify=Gtk.Justification.LEFT
        )
        groups["label"].add_widget(label)
        hbox.pack_start(label, True, True, 6)
        option = VISIBLE.format(self.space)
        self.visible = Gtk.CheckButton(label=_("Visible"))
        self.visible.set_active(self.config.get(option))
        groups["visible"].add_widget(self.visible)
        hbox.pack_start(self.visible, False, False, 6)
        option = APPEND.format(self.space)
        self.append = Gtk.CheckButton(label=_("Append Next Group If Visible"))
        self.append.set_active(self.config.get(option))
        groups["append"].add_widget(self.append)
        hbox.pack_start(self.append, False, False, 6)
        self.set_css_style()

    def drag_data_get(
        self, _dummy_widget, _dummy_context, data, _dummy_info, _dummy_time
    ):
        """
        Return current object identifier.
        """
        data.set_text(str(self.number), -1)

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        css = ".frame { border-width: 0px; }"
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = self.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
