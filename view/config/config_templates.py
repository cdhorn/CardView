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
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.config import config as configman
from gramps.gen.errors import WindowActiveError
from gramps.gui.dialog import ErrorDialog, QuestionDialog2
from gramps.gui.listmodel import NOSORT, ListModel, TOGGLE
from gramps.gui.managedwindow import ManagedWindow

# -------------------------------------------------------------------------
#
# Plugin modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsState
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
# ConfigTemplatesDialog
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
        self.setup_configs("interface.viewconfiguredialog", 420, 500)

    def build_menu_names(self, obj):
        return (self.title, self.title)


# -------------------------------------------------------------------------
#
# ConfigTemplates
#
# -------------------------------------------------------------------------
class ConfigTemplates(Gtk.Box):
    """
    Manage preference templates.
    """

    def __init__(self, configdialog, grstate):
        Gtk.Box.__init__(self, spacing=5, hexpand=True, vexpand=True)
        self.configdialog = configdialog
        self.grstate = grstate
        self.first = True
        self.config_managers = {}
        self.template_list = None
        self.template_model = None
        self._build_layout()
        self._load_layout()

    def _build_layout(self):
        """
        Create widget layout.
        """
        name_titles = [
            (_("Active"), NOSORT, 50, TOGGLE, True, self.cb_set_active),
            (_("Name"), NOSORT, 160),
            ("", NOSORT, 100),  # Untranslated Name
            (_("Description"), NOSORT, 200),
        ]
        self.template_list = Gtk.TreeView()
        self.template_model = ListModel(self.template_list, name_titles)
        slist = Gtk.ScrolledWindow()
        slist.add(self.template_list)
        slist.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(slist, 1, 1, 5)
        bbox = Gtk.ButtonBox(orientation=Gtk.Orientation.VERTICAL)
        bbox.set_layout(Gtk.ButtonBoxStyle.START)
        bbox.set_spacing(6)
        add_button(bbox, _("View Changes"), self.cb_changes_clicked)
        add_button(bbox, _("Copy Template"), self.cb_copy_clicked)
        add_button(bbox, _("Edit Attributes"), self.cb_info_clicked)
        add_button(bbox, _("Edit Template"), self.cb_edit_clicked)
        add_button(bbox, _("Remove Template"), self.cb_remove_clicked)
        add_button(bbox, _("Delete Template"), self.cb_delete_clicked)
        add_button(bbox, _("Import Template"), self.cb_import_clicked)
        self.pack_start(bbox, 0, 0, 5)

    def _load_layout(self):
        """
        Load the layout.
        """
        active_template = self.grstate.templates.get("templates.active")
        name_list = self.grstate.templates.get("templates.templates")
        templates = get_templates(name_list)
        self.template_model.clear()
        self.config_managers.clear()
        for row in sorted(templates):
            (lang, name, desc, ini) = row
            if name == active_template:
                self.template_model.add((True, lang, name, desc))
            else:
                self.template_model.add((False, lang, name, desc))
            self.config_managers.update({name: ini})
        self._select_active()
        self.template_list.show()

    def _select_active(self):
        """
        Find and select active row.
        """
        if self.first:
            store, iter_ = self.template_model.get_selected()
            iter_ = store.get_iter_first()
            while iter_:
                if store.get_value(iter_, 0):
                    selection = self.template_list.get_selection()
                    selection.select_iter(iter_)
                    break
                iter_ = store.iter_next(iter_)
            self.first = False

    def cb_set_active(self, *args):
        """
        Set selection as active template.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 2)
        self.grstate.templates.set("templates.active", name)
        self.grstate.templates.save()
        self._load_layout()
        self.grstate.reload_config(refresh_only=False)

    def cb_copy_clicked(self, button):
        """
        Create a new template by copying from selected one.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        base_name = store.get_value(iter_, 2)
        base_ini = self.config_managers[base_name]
        self.create_template(base_ini)

    def create_template(self, base_ini):
        """
        Create new template copy from old.
        """
        editor = EditTemplateName(self.grstate.uistate, [], "", "")
        result = editor.run()
        if not isinstance(result, tuple):
            return
        (new_name, new_description) = result
        if not new_name:
            return
        template_list = self.grstate.templates.get("templates.templates")
        if new_name in template_list:
            return

        new_template = get_template(new_name)
        (dummy_lang, dummy_name, dummy_description, new_ini) = new_template
        for section in base_ini.get_sections():
            for setting in base_ini.get_section_settings(section):
                key = ".".join((section, setting))
                value = base_ini.get(key)
                default = base_ini.get_default(key)
                new_ini.register(key, default)
                new_ini.set(key, value)
        new_ini.set("template.name_lang", new_name)
        new_ini.set("template.description", new_description)
        new_ini.save()

        template_list.append(new_name)
        template_list.sort()
        self.grstate.templates.set("templates.templates", template_list)
        self.grstate.templates.save()
        self._load_layout()

    def cb_info_clicked(self, button):
        """
        Edit the template name and description.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 2)
        description = store.get_value(iter_, 3)
        ini = self.config_managers[name]
        self._edit_template_info(ini, name, description)

    def cb_edit_clicked(self, button):
        """
        Edit the template options.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        lang = store.get_value(iter_, 1)
        title = " ".join((_("Template Editor:"), lang))
        name = store.get_value(iter_, 2)
        template = self.config_managers[name]
        EditTemplateOptions(
            self.grstate,
            self.configdialog.track,
            template,
            title,
            refresh_only=False,
        )

    def _edit_template_info(self, ini, name, description):
        """
        Edit template name and description.
        """
        editor = EditTemplateName(
            self.grstate.uistate,
            self.configdialog.track,
            name,
            description,
        )
        result = editor.run()
        if isinstance(result, tuple):
            (new_name, new_description) = result
            ini.set("template.name_lang", new_name)
            ini.set("template.description", new_description)
            ini.save()
            self.rename_template(ini, name, new_name)
            self._load_layout()

    def rename_template(self, ini, old_name, new_name):
        """
        If name change rename file to keep it in sync.
        """
        if new_name != old_name:
            old_filename = ini.filename
            dirname = os.path.dirname(old_filename)
            filename = "".join(("Browse_linkview_template_", new_name, ".ini"))
            new_filename = os.path.join(dirname, filename)
            os.replace(old_filename, new_filename)
            ini.filename = new_filename

            template_list = self.grstate.templates.get("templates.templates")
            template_list.remove(old_name)
            template_list.append(new_name)
            template_list.sort()
            self.grstate.templates.set("templates.templates", template_list)
            self.grstate.templates.save()

    def cb_remove_clicked(self, button):
        """
        Remove the selected template.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 2)
        if name == "Default":
            return

        name_lang = store.get_value(iter_, 1)
        yes_no = QuestionDialog2(
            _("Remove template '%s'?") % name_lang,
            _("The template will be removed but not deleted from disk."),
            _("Yes"),
            _("No"),
        )
        prompt = yes_no.run()
        if prompt:
            self.remove_template(name)

    def cb_delete_clicked(self, button):
        """
        Delete the selected template.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 2)
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
            self.remove_template(name, delete=True)

    def remove_template(self, name, delete=False):
        """
        Remove template and optionally delete from disk.
        """
        active_template = self.grstate.templates.get("templates.active")
        if name == active_template:
            self.grstate.templates.set("templates.active", "Default")
        template_list = self.grstate.templates.get("templates.templates")
        template_list.remove(name)
        template_list.sort()
        self.grstate.templates.set("templates.templates", template_list)
        self.grstate.templates.save()
        if delete:
            ini = self.config_managers[name]
            os.remove(ini.filename)
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

    def cb_changes_clicked(self, button):
        """
        View changes against defaults.
        """
        store, iter_ = self.template_model.get_selected()
        if iter_ is None:
            return

        name = store.get_value(iter_, 2)
        TemplateChangeViewer(self.grstate, name)


# -------------------------------------------------------------------------
#
# EditTemplateName
#
# -------------------------------------------------------------------------
class EditTemplateName(ManagedWindow):
    """
    A dialog to enable the user to edit a template name and description.
    """

    def __init__(self, uistate, track, name, description=""):
        if name:
            self.title = _("Template: %s") % name
        else:
            self.title = _("New Template")
        ManagedWindow.__init__(
            self, uistate, track, self.__class__, modal=True
        )
        # the self.top.run() below makes Gtk make it modal, so any change to
        # the previous line's "modal" would require that line to be changed
        self.top = None
        self.name = name
        self.name_entry = None
        self.description = description
        self.description_entry = None

    def build_menu_names(self, obj):  # this is meaningless while it's modal
        return (self.title, None)

    def run(self):
        """
        Run the dialog and return the result.
        """
        self.top = self._create_dialog()
        self.set_window(self.top, None, self.title)
        self.setup_configs("interface.edit_template", 320, 100)
        self.show()
        while True:
            # the self.top.run() makes Gtk make it modal, so any change to that
            # line would require the ManagedWindow.__init__ to be changed also
            response = self.top.run()
            if response == Gtk.ResponseType.OK:
                name = self.name_entry.get_text()
                if self.check_name_valid(name):
                    description = self.description_entry.get_text() or ""
                    self.close()
                    return (name, description)
            else:
                break
        self.close()
        return None

    def check_name_valid(self, name):
        """
        Sanity check the name entered.
        """
        if not name:
            ErrorDialog(
                _("Invalid name field"),
                _("The name cannot be empty"),
                parent=self.window,
            )
            return False
        if not name.isalnum():
            ErrorDialog(
                _("Invalid name field"),
                _("Only alphanumeric characters are permitted in the name"),
                parent=self.window,
            )
            return False
        return True

    def _create_dialog(self):
        """
        Create a dialog box to enter a new name and description.
        """
        top = Gtk.Dialog(transient_for=self.parent_window)
        top.vbox.set_spacing(5)
        group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)
        hbox = Gtk.Box()
        top.vbox.pack_start(hbox, False, False, 10)
        label = Gtk.Label(label=_("Template Name:"))
        group.add_widget(label)
        self.name_entry = Gtk.Entry()
        if self.name:
            self.name_entry.set_text(self.name)
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(self.name_entry, True, True, 5)
        hbox = Gtk.Box()
        top.vbox.pack_start(hbox, False, False, 10)
        label = Gtk.Label(label=_("Description:"))
        group.add_widget(label)
        self.description_entry = Gtk.Entry()
        if self.description:
            self.description_entry.set_text(self.description)
        hbox.pack_start(label, False, False, 5)
        hbox.pack_start(self.description_entry, True, True, 5)
        top.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        top.add_button(_("_OK"), Gtk.ResponseType.OK)
        return top


# -------------------------------------------------------------------------
#
# EditTemplateOptions
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
        ident = "".join((_("Template"), ": ", ident, " - ", _("Linked")))
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
        Always skip active.last_object as otherwise triggers a second redraw.
        """
        for section in self.template.get_sections():
            for setting in self.template.get_section_settings(section):
                key = ".".join((section, setting))
                if "active.last_object" not in key and "layout" not in key:
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
# ImportTemplateSelector
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
        self.setup_configs("interface.linked-view.import-template", 780, 630)
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
            ini = configman.register_manager(
                filename,
                use_config_path=False,
                use_plugins_path=False,
            )
            for key, value in VIEWDEFAULTS:
                ini.register(key, value)
            ini.load()
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
# ViewTemplateChanges
#
# -------------------------------------------------------------------------
class TemplateChangeViewer(ManagedWindow):
    """
    Display differences between default, template and active database options.
    """

    def __init__(self, grstate, name):
        """
        A dialog to view template changes.
        """
        (lang, dummy_name, dummy_description, ini) = get_template(name)
        self.ini = ini
        self.title = "".join(
            (_("Template Change View"), ": ", lang, " ", _("Template"))
        )
        ManagedWindow.__init__(
            self, grstate.uistate, [], self.__class__, modal=True
        )
        # the import_dialog.run() below makes it modal, so any change to
        # the previous line's "modal" would require that line to be changed

        self.grstate = grstate
        self.column_list = None
        self.column_model = None
        self.top, self.header = self.create_dialog()
        self.set_window(self.top, None, self.title)
        self.setup_configs(
            "interface.linked-view.template-change-viewer", 320, 100
        )
        self.load_data()
        self.show()
        self.top.run()
        self.close()

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
            (_("Default"), NOSORT, 160),
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
            _("Template Name:"),
            ini.get("template.name_lang"),
            ini.filename,
        )
        add_header(
            self.header,
            group,
            _("Database Baseline:"),
            config.get("template.name_lang"),
            config.filename,
        )
        for key, default_value in VIEWDEFAULTS:
            default_value = str(default_value)
            template_value = str(ini.get(key))
            if template_value == default_value:
                template_value = ""
            database_value = str(config.get(key))
            if template_value and database_value == template_value:
                database_value = ""
            elif not template_value and database_value == default_value:
                database_value = ""
            self.column_model.add(
                (key, default_value, template_value, database_value)
            )
        self.column_list.show()

    def build_menu_names(self, obj):  # this is meaningless since it's modal
        return (self.title, None)


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


def add_button(box, label, callback):
    """
    Add button to a button box.
    """
    button = Gtk.Button.new_with_label(label)
    button.connect("clicked", callback)
    box.add(button)


def get_templates(name_list):
    """
    Collect the templates.
    """
    templates = []
    for name in name_list:
        template = get_template(name)
        templates.append(template)
    return templates


def get_template(name):
    """
    Get a template.
    """
    ini_name = "_".join(("Browse_linkview_template", name))
    if configman.has_manager(ini_name):
        ini = configman.get_manager(ini_name)
    else:
        ini = configman.register_manager(
            ini_name,
            use_config_path=True,
            use_plugins_path=False,
        )
        for key, value in VIEWDEFAULTS:
            ini.register(key, value)
        ini.load()
    if not ini.get("template.name_lang"):
        ini.set("template.name_lang", name)
    lang = ini.get("template.name_lang")
    if not ini.get("template.description"):
        ini.set("template.description", " ".join((lang, _("Template"))))
    description = ini.get("template.description")
    ini.save()
    return (lang, name, description, ini)
