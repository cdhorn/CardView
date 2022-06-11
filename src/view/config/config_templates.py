#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2005-2007  Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Nick Hall
# Copyright (C) 2022       Christopher Horn
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
Template manager functionality.
"""

import os

# -------------------------------------------------------------------------
#
# GTK Modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as configman
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.dialog import ErrorDialog, QuestionDialog2
from gramps.gui.display import display_url
from gramps.gui.listmodel import NOSORT, TOGGLE, ListModel
from gramps.gui.managedwindow import ManagedWindow

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsState
from ..services.service_templates import TemplatesService
from .config_const import HELP_CONFIG_TEMPLATES
from .config_defaults import VIEWDEFAULTS
from .config_layout import build_layout_grid
from .config_panel import (
    build_color_panel,
    build_global_panel,
    build_object_panel,
    build_timeline_panel,
)
from .configure_dialog import ModifiedConfigureDialog

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# ConfigTemplatesDialog Class
#
# This is mostly ViewConfigureDialog but lets us pass window tracking
# through
#
# -------------------------------------------------------------------------
class ConfigTemplatesDialog(ModifiedConfigureDialog):
    """
    All views can have their own configuration dialog
    """

    def __init__(
        self,
        uistate,
        dbstate,
        track,
        configure_page_funcs,
        configobj,
        configmanager,
        dialogtitle,
        on_close=None,
    ):
        self.title = dialogtitle
        ModifiedConfigureDialog.__init__(
            self,
            uistate,
            dbstate,
            track,
            configure_page_funcs,
            configobj,
            configmanager,
            dialogtitle=dialogtitle,
            on_close=on_close,
        )
        self.setup_configs(
            "interface.cardview.view-configuration-dialog", 420, 500
        )

    def build_menu_names(self, obj):
        return (self.title, self.title)


# -------------------------------------------------------------------------
#
# ConfigTemplates Class
#
# -------------------------------------------------------------------------
class ConfigTemplates(Gtk.HBox):
    """
    Manage preference templates.
    """

    def __init__(self, configdialog, grstate):
        Gtk.HBox.__init__(self, spacing=5, hexpand=False, vexpand=True)
        self.set_margin_right(0)
        self.configdialog = configdialog
        self.grstate = grstate
        self.selected = None
        self.templates_service = TemplatesService(self.grstate.dbstate)
        self.template_list = None
        self.template_model = None
        self.delete_button = self._build_layout()
        self._load_layout()

    def _build_layout(self):
        """
        Create widget layout.
        """
        name_titles = [
            (_("Active"), NOSORT, 50, TOGGLE, True, self.cb_set_active),
            (_("Name"), NOSORT, 80),  # Lang
            (_("Description"), NOSORT, 200),
            (_("Normal Baseline"), NOSORT, 120),
            (_("Active Baseline"), NOSORT, 120),
            ("", NOSORT, 0),  # Untranslated Name
        ]
        self.template_list = Gtk.TreeView()
        self.template_model = ListModel(self.template_list, name_titles)
        self.template_list.connect("cursor-changed", self._toggle_buttons)
        self.pack_start(self.template_list, 0, 0, 0)
        grid = Gtk.Grid(hexpand=False, vexpand=False)
        add_button(grid, 0, _("Edit Template"), self.cb_edit_clicked)
        add_button(grid, 1, _("View Changes"), self.cb_changes_clicked)
        add_button(grid, 2, _("Copy Template"), self.cb_copy_clicked)
        add_button(grid, 3, _("Rename Template"), self.cb_rename_clicked)
        delete = add_button(
            grid, 4, _("Delete Template"), self.cb_delete_clicked
        )
        add_button(grid, 5, _("Import Template"), self.cb_import_clicked)
        add_button(grid, 6, _("Help"), self.cb_help_clicked)
        self.pack_start(grid, 0, 0, 0)
        return delete

    def _load_layout(self):
        """
        Load the layout.
        """
        active_template = self.grstate.templates.get("templates.active")
        templates = self.templates_service.get_templates()
        templates.sort(key=lambda x: x["lang_string"])
        self.template_model.clear()
        for template in templates:
            if template["xml_string"] == active_template:
                flag = True
                if not self.selected:
                    self.selected = template["xml_string"]
            else:
                flag = False
            self.template_model.add(
                (
                    flag,
                    template["lang_string"],
                    template["description"],
                    template["normal_baseline"],
                    template["active_baseline"],
                    template["xml_string"],
                )
            )
        self._select_active()
        self.template_list.show()
        self.template_list.columns_autosize()

    def _select_active(self):
        """
        Find and select active row.
        """
        iter_active = None
        store, iter_ = self.template_model.get_selected()
        iter_ = store.get_iter_first()
        while iter_:
            if store.get_value(iter_, 0):
                iter_active = iter_
            if store.get_value(iter_, 5) == self.selected:
                break
            iter_ = store.iter_next(iter_)
        if not iter_:
            iter_ = iter_active
        selection = self.template_list.get_selection()
        if selection:
            selection.select_iter(iter_)
            self.selected = store.get_value(iter_, 5)
        self._toggle_buttons()

    def _toggle_buttons(self, *_dummy_args):
        """
        Toggle button state if Default.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        if store.get_value(iter_, 5) == "Default":
            self.delete_button.set_sensitive(False)
        else:
            self.delete_button.set_sensitive(True)

    def cb_set_active(self, *args):
        """
        Set selection as active template.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 5)
        self.grstate.templates.set("templates.active", name)
        self.grstate.templates.save()
        self._load_layout()
        self.grstate.reload_config(refresh_only=False)

    def cb_edit_clicked(self, button):
        """
        Edit the template options.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        lang = store.get_value(iter_, 1)
        title = " ".join((_("Template Editor:"), lang))
        name = store.get_value(iter_, 5)
        (
            _dummy_name,
            template,
        ) = self.templates_service.get_rebased_user_options(name)
        EditTemplateOptions(
            self.grstate,
            self.configdialog.track,
            template,
            title,
            refresh_only=False,
        )

    def cb_changes_clicked(self, button):
        """
        View changes against defaults.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 5)
        TemplateChangeViewer(self.grstate, self.configdialog.track, name)

    def cb_copy_clicked(self, button):
        """
        Create a new template by copying a selected one.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        base_name = store.get_value(iter_, 5)
        used_names = self.templates_service.get_template_names()
        new_name_dialog = GetNewTemplateNameDialog(
            self.grstate.uistate,
            self.configdialog.track,
            used_names=used_names,
        )
        new_name = new_name_dialog.run()
        if isinstance(new_name, str):
            self.templates_service.copy_template(base_name, new_name)
            self.selected = base_name
            self._load_layout()

    def cb_rename_clicked(self, button):
        """
        Rename an existing template.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        base_name = store.get_value(iter_, 5)
        used_names = self.templates_service.get_template_names()
        new_name_dialog = GetNewTemplateNameDialog(
            self.grstate.uistate,
            self.configdialog.track,
            used_names=used_names,
        )
        new_name = new_name_dialog.run()
        if isinstance(new_name, str):
            self.templates_service.rename_template(base_name, new_name)
            self.selected = new_name
            self._load_layout()

    def cb_delete_clicked(self, button):
        """
        Delete the selected template.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 5)
        if name == "Default":
            return

        name_lang = store.get_value(iter_, 1)
        yes_no = QuestionDialog2(
            _("Delete template '%s'?") % name_lang,
            _("The template will be permanently deleted."),
            _("Yes"),
            _("No"),
        )
        prompt = yes_no.run()
        if prompt:
            self.templates_service.delete_template(name)
            self.selected = None
            self._load_layout()

    def cb_import_clicked(self, button):
        """
        Import a template.
        """
        import_selector = ImportTemplateSelector(self.grstate.uistate, [])
        filename = import_selector.run()
        if isinstance(filename, str):
            if configman.has_manager(filename):
                import_ini = configman.get_manager(filename)
            else:
                import_ini = configman.register_manager(
                    filename,
                    use_config_path=False,
                    use_plugins_path=False,
                )
                for key, value in VIEWDEFAULTS:
                    import_ini.register(key, value)
                import_ini.load()
            self.create_template(import_ini)

    def cb_help_clicked(self, button):
        """
        Launch template editor help
        """
        display_url(HELP_CONFIG_TEMPLATES)


# -------------------------------------------------------------------------
#
# GetNewTemplateName Class
#
# -------------------------------------------------------------------------
class GetNewTemplateNameDialog(ManagedWindow):
    """
    A dialog to get a new template name from a user.
    """

    def __init__(self, uistate, track, used_names=None):
        self.title = _("New Template Name")
        ManagedWindow.__init__(
            self, uistate, track, self.__class__, modal=True
        )
        # the self.top.run() below makes Gtk make it modal, so any change to
        # the previous line's "modal" would require that line to be changed
        self.top = None
        self.name_entry = None
        self.used_names = used_names or []

    def build_menu_names(self, obj):  # this is meaningless while it's modal
        return (self.title, None)

    def run(self):
        """
        Run the dialog and return the result.
        """
        self.top = self._create_dialog()
        self.set_window(self.top, None, self.title)
        self.setup_configs(
            "interface.cardview.new-template-name-modal", 320, 100
        )
        self.show()
        while True:
            # the self.top.run() makes Gtk make it modal, so any change to that
            # line would require the ManagedWindow.__init__ to be changed also
            response = self.top.run()
            if response == Gtk.ResponseType.OK:
                name = self.name_entry.get_text()
                if self.check_name_valid(name):
                    self.close()
                    return name
            elif response == Gtk.ResponseType.CANCEL:
                self.close()
                return None
            else:
                break
        return None

    def check_name_valid(self, name):
        """
        Sanity check the name entered.
        """
        error_message = None
        if not name:
            error_message = _("The name cannot be empty")
        elif not name.isalnum():
            error_message = _(
                "Only a single word with alphanumeric characters is permitted"
            )
        elif name in self.used_names:
            error_message = _("The name is already in use")
        if error_message:
            ErrorDialog(_("Invalid name"), error_message, parent=self.window)
            return False
        return True

    def _create_dialog(self):
        """
        Create a dialog box to enter a new name and description.
        """
        top = Gtk.Dialog(transient_for=self.parent_window)
        top.vbox.set_spacing(5)
        hbox = Gtk.Box()
        top.vbox.pack_start(hbox, False, False, 10)
        label = Gtk.Label(label=_("New Template Name:"))
        self.name_entry = Gtk.Entry()
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(self.name_entry, True, True, 5)
        top.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        top.add_button(_("_OK"), Gtk.ResponseType.OK)
        return top


# -------------------------------------------------------------------------
#
# EditTemplateOptions Class
#
# -------------------------------------------------------------------------
class EditTemplateOptions:
    """
    Editor for all the options in a given template.
    """

    def __init__(
        self, grstate, track, template, title, panels=None, refresh_only=True
    ):
        panels = panels or [
            self.global_panel,
            self.layout_panel,
            self.active_panel,
            self.group_panel,
            self.timeline_panel,
            self.color_panel,
        ]
        self.refresh_only = refresh_only
        self.grstate = GrampsState(
            grstate.dbstate, grstate.uistate, grstate.callbacks, template
        )
        self.template = template
        self.config_callback_ids = []
        self.config_connect()
        ident = title.split(":").pop(-1).strip()
        ident = "".join((_("Template"), ": ", ident, " - ", _("Card")))
        try:
            ConfigTemplatesDialog(
                grstate.uistate,
                grstate.dbstate,
                track,
                panels,
                template,
                template,
                title,
            )
        except WindowActiveError:
            self.config_disconnect()

    def config_connect(self):
        """
        Connect configuration callbacks so can update on changes.
        """
        for section in self.template.get_sections():
            for setting in self.template.get_section_settings(section):
                key = ".".join((section, setting))
                if "layout" not in key:
                    try:
                        callback_id = self.template.connect(
                            key, self.config_refresh
                        )
                        self.config_callback_ids.append(callback_id)
                    except KeyError:
                        pass

    def config_refresh(self, *_dummy_args):
        """
        Force a top level config refresh.
        """
        self.template.save()
        self.grstate.reload_config(refresh_only=self.refresh_only)

    def config_disconnect(self):
        """
        Disconnect configuration callbacks.
        """
        for callback_id in self.config_callback_ids:
            self.template.disconnect(callback_id)
        self.config_callback_ids.clear()

    def global_panel(self, configdialog):
        """
        Build global options panel for the configuration dialog.
        """
        return _("Global"), build_global_panel(configdialog, self.grstate)

    def layout_panel(self, configdialog):
        """
        Build layout panel for the configuration dialog.
        """
        return _("Layout"), build_layout_grid(configdialog, self.grstate)

    def active_panel(self, configdialog):
        """
        Build active object options panel for the configuration dialog.
        """
        return _("Active"), build_object_panel(
            configdialog, self.grstate, "active"
        )

    def group_panel(self, configdialog):
        """
        Build object group options panel for the configuration dialog.
        """
        return _("Groups"), build_object_panel(
            configdialog, self.grstate, "group"
        )

    def timeline_panel(self, configdialog):
        """
        Build timeline options panel for the configuration dialog.
        """
        return _("Timelines"), build_timeline_panel(configdialog, self.grstate)

    def color_panel(self, configdialog):
        """
        Build color scheme options panel for the configuration dialog.
        """
        return _("Colors"), build_color_panel(configdialog, self.grstate)


# -------------------------------------------------------------------------
#
# ImportTemplateSelector Class
#
# -------------------------------------------------------------------------
class ImportTemplateSelector(ManagedWindow):
    """
    Selector for picking an import file.
    """

    def __init__(self, uistate, track):
        """
        A dialog to import a template into Gramps
        """
        self.title = _("Import Template")
        ManagedWindow.__init__(
            self, uistate, track, self.__class__, modal=True
        )
        # the import_dialog.run() below makes it modal, so any change to
        # the previous line's "modal" would require that line to be changed

    def run(self):
        """
        Get the selection.
        """
        import_dialog = Gtk.FileChooserDialog(
            title="",
            transient_for=self.uistate.window,
            action=Gtk.FileChooserAction.OPEN,
        )
        import_dialog.add_buttons(
            _("_Cancel"),
            Gtk.ResponseType.CANCEL,
            _("Import"),
            Gtk.ResponseType.OK,
        )
        self.set_window(import_dialog, None, self.title)
        self.setup_configs(
            "interface.cardview.import-template-modal", 780, 630
        )
        import_dialog.set_local_only(False)

        file_filter = Gtk.FileFilter()
        file_filter.add_pattern("*.%s" % icase("ini"))
        import_dialog.add_filter(file_filter)

        import_dialog.set_current_folder(
            configman.get("paths.recent-import-dir")
        )
        while True:
            # the import_dialog.run() makes it modal, so any change to that
            # line would require the ManagedWindow.__init__ to be changed also
            response = import_dialog.run()
            if response == Gtk.ResponseType.CANCEL:
                break
            if response == Gtk.ResponseType.DELETE_EVENT:
                return
            if response == Gtk.ResponseType.OK:
                filename = import_dialog.get_filename()
                if self.check_errors(filename):
                    # displays errors if any
                    continue
                self.close()
                return filename
        self.close()

    def check_errors(self, filename):
        """
        Run common error checks and return True if any found.
        """
        if not isinstance(filename, str):
            return True

        filename = os.path.normpath(os.path.abspath(filename))

        if len(filename) == 0:
            return True
        if os.path.isdir(filename):
            ErrorDialog(
                _("Cannot open file"),
                _("The selected file is a directory, not a file.\n"),
                parent=self.uistate.window,
            )
            return True
        if os.path.exists(filename) and not os.access(filename, os.R_OK):
            ErrorDialog(
                _("Cannot open file"),
                _("You do not have read access to the selected file."),
                parent=self.uistate.window,
            )
            return True
        try:
            load_user_ini_file(filename)
        except:
            ErrorDialog(
                _("Error loading file data"),
                _("May not be in valid format."),
                parent=self.uistate.window,
            )
            return True
        return False

    def build_menu_names(self, obj):  # this is meaningless since it's modal
        return (self.title, None)


# -------------------------------------------------------------------------
#
# ViewTemplateChanges Class
#
# -------------------------------------------------------------------------
class TemplateChangeViewer(ManagedWindow):
    """
    Display differences between default, template and active database options.
    """

    def __init__(self, grstate, track, name):
        """
        A dialog to view template changes.
        """
        self.templates_service = TemplatesService(grstate.dbstate)
        (
            _dummy_name,
            template,
        ) = self.templates_service.get_rebased_user_options(name)
        lang, self.ini = template.get("template.xml_string"), template
        self.title = "".join(
            (_("Template Change View"), ": ", lang, " ", _("Template"))
        )
        ManagedWindow.__init__(
            self, grstate.uistate, track, self.__class__, modal=True
        )
        self.grstate = grstate
        self.column_list = None
        self.column_model = None
        self.top, self.header = self.create_dialog()
        self.set_window(self.top, None, self.title)
        self.setup_configs(
            "interface.cardview.template-change-viewer-modal", 320, 100
        )
        self.load_data()
        self.show()
        self.top.run()

    def create_dialog(self):
        """
        Create a dialog box to display the data.
        """
        top = Gtk.Dialog(transient_for=self.parent_window)
        top.vbox.set_spacing(5)
        header = Gtk.VBox(hexpand=False, vexpand=False)
        top.vbox.pack_start(header, False, False, 3)
        column_titles = [
            (_("Option"), NOSORT, 300),
            (_("Baseline"), NOSORT, 160),
            (_("Template"), NOSORT, 160),
            (_("Database"), NOSORT, 160),
        ]
        self.column_list = Gtk.TreeView()
        self.column_model = ListModel(self.column_list, column_titles)
        slist = Gtk.ScrolledWindow()
        slist.add(self.column_list)
        slist.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        top.vbox.pack_start(slist, True, True, 3)
        return top, header

    def load_data(self):
        """
        Load the layout.
        """
        ini = self.ini
        config = self.grstate.config
        group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        add_header(
            self.header,
            group,
            _("Active User Template:"),
            ini.get("template.lang_string"),
            ini.filename,
        )
        add_header(
            self.header,
            group,
            _("Active Database Template:"),
            config.get("template.lang_string"),
            config.filename,
        )
        active_baseline = ini.get("template.active_baseline")
        (
            baseline_name,
            baseline_options,
        ) = self.templates_service.get_baseline_options(active_baseline)
        load_change_model(self.column_model.add, baseline_options, ini, config)
        self.column_list.show()

    def build_menu_names(self, obj):  # this is meaningless since it's modal
        return (self.title, None)


def load_change_model(add_model, defaults_list, ini, config):
    """
    Load options and changes into the model.
    """
    for key, default_value in defaults_list:
        default_value = str(default_value)
        template_value = str(ini.get(key))
        if template_value == default_value:
            template_value = ""
        database_value = str(config.get(key))
        if template_value and database_value == template_value:
            database_value = ""
        elif not template_value and database_value == default_value:
            database_value = ""
        add_model((key, default_value, template_value, database_value))


def add_header(widget, group, label1, label2, label3):
    """
    Add header entry to widget.
    """
    hbox = Gtk.HBox(hexpand=False)
    label = Gtk.Label(
        label=label1,
        xalign=0.0,
        justify=Gtk.Justification.LEFT,
        halign=Gtk.Align.START,
    )
    hbox.pack_start(label, False, False, 3)
    label = Gtk.Label(
        label=label2,
        xalign=0.0,
        justify=Gtk.Justification.LEFT,
        halign=Gtk.Align.START,
    )
    group.add_widget(label)
    hbox.pack_start(label, False, False, 3)
    label = Gtk.Label(
        label=label3, justify=Gtk.Justification.RIGHT, halign=Gtk.Align.END
    )
    hbox.pack_end(label, True, True, 6)
    widget.pack_start(hbox, True, True, 0)


def icase(ext):
    """
    Return a glob reresenting a case insensitive file extension.
    """
    return "".join(["[{}{}]".format(s.lower(), s.upper()) for s in ext])


def build_templates_panel(configdialog, grstate):
    """
    Build templates manager grid for the configuration dialog.
    """
    grid = Gtk.Grid(
        row_spacing=6,
        column_spacing=6,
        column_homogeneous=False,
        margin_bottom=12,
        margin_top=6,
        margin_left=6,
        hexpand=False,
        vexpand=False,
    )
    configdialog.add_text(grid, _("Preference Templates"), 0, bold=True)
    templates = ConfigTemplates(configdialog, grstate)
    grid.attach(templates, 1, 1, 1, 1)
    return grid


def add_button(grid, column, label, callback):
    """
    Add button to a button box.
    """
    button = Gtk.Button.new_with_label(label)
    button.connect("clicked", callback)
    button.set_margin_bottom(5)
    grid.attach(button, 0, column, 1, 1)
    return button
