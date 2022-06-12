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
TemplatesService
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import os

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as configman
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import VERSION_DIR
from gramps.gen.plug import BasePluginManager

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..config.config_defaults import VIEWDEFAULTS
from ..config.config_const import BASE_TEMPLATE_NAME
from .service_fields import FieldCalculatorService
from .service_status import StatusIndicatorService

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# TemplatesService
#
# -------------------------------------------------------------------------
class TemplatesService:
    """
    A singleton class that manages template access.
    """

    __init = False

    def __new__(cls, *args):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(TemplatesService, cls).__new__(cls)
        return cls.instance

    def __init__(self, dbstate):
        if not self.__init:
            self.dbstate = dbstate
            self.plugin_manager = BasePluginManager.get_instance()
            self.template_directory = os.path.join(VERSION_DIR, "templates")
            if not os.path.isdir(self.template_directory):
                os.mkdir(self.template_directory)
            self.templates = {}
            self.load_templates()
            self.load_baseline_plugins()
            self.__init = True

    def load_baseline_plugins(self):
        """
        Load baseline template plugins and insure template exists for each.
        """
        self.plugin_manager.load_plugin_category("TEMPLATE")
        plugin_data = self.plugin_manager.get_plugin_data("TEMPLATE")
        for plugin in plugin_data:
            template_name = plugin["name"]
            if template_name not in self.templates:
                template_file_name = self.get_template_path(template_name)
                ini = self.get_template_config_manager(
                    template_name, template_file_name
                )
                baseline_options = plugin["options"]
                baseline_options = merge_defaults(
                    baseline_options, StatusIndicatorService().get_defaults()
                )
                baseline_options = merge_defaults(
                    baseline_options, FieldCalculatorService().get_defaults()
                )
                ini = register_default_options(ini, baseline_options)
                ini.set("template.normal_baseline", template_name)
                ini.set("template.active_baseline", template_name)
                self.save_template(ini)

    def load_templates(self):
        """
        Scan template directory and load metadata for templates found.
        """
        self.templates = {}
        for object_name in os.listdir(self.template_directory):
            if object_name[:18] != "CardView_template_":
                continue
            file_name = os.path.join(self.template_directory, object_name)
            if not os.path.isfile(file_name):
                continue
            data = parse_template(file_name)
            if data and data["xml_string"] not in self.templates:
                data["file_name"] = file_name
                self.templates[data["xml_string"]] = data

    def get_template_names(self):
        """
        Return list of available templates.
        """
        self.load_templates()
        return list(self.templates.keys())

    def get_templates(self):
        """
        Return the template metadata.
        """
        self.load_templates()
        return list(self.templates.values())

    def get_template(self, template_name):
        """
        Return the template metadata.
        """
        return self.templates.get(template_name)

    def get_template_path(self, template_name, db=False):
        """
        Construct template path.
        """
        if db:
            template_type = "_database_"
        else:
            template_type = "_template_"
        full_template_name = "".join(
            (BASE_TEMPLATE_NAME, template_type, template_name, ".ini")
        )
        return os.path.join(self.template_directory, full_template_name)

    def get_template_config_manager(self, template_name, template_file_name):
        """
        Get config manage instance for a template.
        """
        ini = configman.register_manager(
            template_name, override=template_file_name, use_plugins_path=False
        )
        ini.register("template.normal_baseline", "")
        ini.register("template.active_baseline", "")
        return ini

    def get_rebased_user_options(self, template_name):
        """
        Load and return a rebased user template.
        """
        template_file_name = self.get_template_path(template_name)
        if not os.path.isfile(template_file_name):
            template_name = "Default"
            template_file_name = self.get_template_path(template_name)
        ini = self.get_template_config_manager(
            template_name, template_file_name
        )
        ini.load()
        normal_baseline = ini.get("template.normal_baseline")
        if not normal_baseline:
            normal_baseline = "Default"
        baseline_name, baseline_options = self.get_baseline_options(
            normal_baseline
        )
        ini = register_default_options(ini, baseline_options)
        if not ini.get("template.normal_baseline"):
            ini.set("template.normal_baseline", normal_baseline)
        ini.set("template.active_baseline", baseline_name)
        self.save_template(ini)
        return template_name, ini

    def get_rebased_database_options(self, user_options):
        """
        Load and return a rebased database template.
        """
        if self.dbstate.is_open():
            dbid = self.dbstate.db.get_dbid()
            template_file_name = self.get_template_path(dbid, db=True)
            ini = self.get_template_config_manager(dbid, template_file_name)
            ini = register_default_options(ini, user_options)
            self.save_template(ini)
            return ini
        return None

    def get_baseline_names(self):
        """
        Return list of available template baselines.
        """
        baseline_names = ["Default"]
        self.plugin_manager.load_plugin_category("TEMPLATE")
        plugin_data = self.plugin_manager.get_plugin_data("TEMPLATE")
        for plugin in plugin_data:
            baseline_names.append(plugin["name"])
        return baseline_names

    def get_baseline_options(self, template_name):
        """
        Get baseline template options.
        """
        baseline_options = VIEWDEFAULTS
        baseline_name = "Default"
        if template_name != "Default":
            self.plugin_manager.load_plugin_category("TEMPLATE")
            plugin_data = self.plugin_manager.get_plugin_data("TEMPLATE")
            for plugin in plugin_data:
                if plugin["name"] == template_name:
                    baseline_options = plugin["options"]
                    baseline_name = template_name
                    break
        baseline_options = merge_defaults(
            baseline_options, StatusIndicatorService().get_defaults()
        )
        baseline_options = merge_defaults(
            baseline_options, FieldCalculatorService().get_defaults()
        )
        return baseline_name, baseline_options

    def save_template(self, config):
        """
        Save template, rewriting header as needed.
        """
        config.save()
        if config.is_set("template.comments"):
            comments = config.get("template.comments")
            if comments:
                rewrite_template(config.filename, comments)

    def copy_template(self, base_name, new_name):
        """
        Create a new copy of a template.
        """
        if configman.has_manager(base_name):
            base_ini = configman.get_manager(base_name)
        else:
            base_ini = self.get_rebased_user_options(base_name)

        new_ini_file_name = self.get_template_path(new_name)
        new_ini = self.get_template_config_manager(new_name, new_ini_file_name)
        for section in base_ini.get_sections():
            for setting in base_ini.get_section_settings(section):
                key = ".".join((section, setting))
                try:
                    value = base_ini.get(key)
                    default = base_ini.get_default(key)
                except AttributeError:
                    continue
                new_ini.register(key, default)
                new_ini.set(key, value)
        comment = "%s %s" % (
            _("Copy of"),
            base_ini.get("template.lang_string"),
        )
        new_ini.set("template.lang_string", new_name)
        new_ini.set("template.xml_string", new_name)
        new_ini.set("template.description", comment)
        new_ini.set("template.comments", [comment])
        self.save_template(new_ini)

    def rename_template(self, old_name, new_name):
        """
        Rename an existing template.
        """
        if configman.has_manager(old_name):
            manager = configman.get_manager(old_name)
        else:
            manager = None
        old_file_name = self.get_template_path(old_name)
        new_file_name = self.get_template_path(new_name)
        os.replace(old_file_name, new_file_name)
        # This is clearly ugly...
        if manager:
            manager.filename = new_file_name
        else:
            _dummy_name, manager = self.get_rebased_user_options(new_name)
        manager.set("template.xml_string", new_name)
        manager.set("template.lang_string", new_name)
        self.save_template(manager)
        configman.register_manager(new_name, override=manager)

    def delete_template(self, template_name):
        """
        Delete template.
        """
        file_name = self.get_template_path(template_name)
        os.remove(file_name)

    def validate_template_file(self, file_name):
        """
        Validate a file is a valid template file.
        """
        try:
            data = parse_template(file_name)
        except TypeError:
            return False
        for key in [
            "xml_string",
            "lang_string",
            "type",
            "normal_baseline",
            "active_baseline",
            "description",
            "comments",
        ]:
            if key not in data:
                return False
        return True

    def import_template_file(self, file_name, template_name):
        """
        Import a template, which is just a copy then rename.
        """
        new_file_name = self.get_template_path(template_name)
        with open(file_name, "r") as import_file:
            data = import_file.read()
        with open(new_file_name, "w") as new_file:
            new_file.write(data)
        _dummy_name, manager = self.get_rebased_user_options(template_name)
        manager.set("template.xml_string", template_name)
        manager.set("template.lang_string", template_name)
        self.save_template(manager)
        configman.register_manager(template_name, override=manager)


def parse_template(file_name):
    """
    Parse a template to extract template metadata.
    """
    with open(file_name, "r") as file_handle:
        template_data = file_handle.read()

    data = {}
    comments = []
    in_header = True
    line_count = 0
    in_section = False
    for line in template_data.split("\n"):
        if in_header:
            if line_count < 3:
                if line_count == 0 and line != ";; Gramps key file":
                    raise TypeError("Not a Gramps key file: %s" % file_name)
                line_count = line_count + 1
                continue
            if line[:1] == "[":
                in_header = False
                continue
            if line[:3] == ";; ":
                comments.append(line[3:].strip())
                continue
        if line[:10] == "[template]":
            in_section = True
            continue
        if in_section:
            if not line.strip():
                break
            key, value = line.strip("; ").split("=")
            data[key] = value.strip("'")

    if not in_section:
        return None
    data["comments"] = comments
    return data


def rewrite_template(file_name, comments):
    """
    Rewrite template to save additional comments.
    """
    with open(file_name, "r") as old_file:
        template_data = old_file.read()

    comments_written = False
    work_file_name = "%s.new" % file_name
    with open(work_file_name, "w") as new_file:
        for line in template_data.split("\n"):
            if not comments_written:
                if line[:3] == ";; ":
                    new_file.write("%s\n" % line)
                else:
                    new_file.write("\n")
                    for comment in comments:
                        new_file.write(";; %s\n" % comment)
                    new_file.write("\n")
                    comments_written = True
                continue
            new_file.write("%s\n" % line)
    os.replace(work_file_name, file_name)


def merge_defaults(options, defaults):
    """
    Merge two sets of default values.
    """
    options = list(options)
    for (key, value) in defaults:
        found = False
        for (option_key, _option_value) in options:
            if option_key == key:
                found = True
                break
        if not found:
            options = options + [(key, value)]
    return tuple(options)


def find_option_value(options, search_key):
    """
    Return option value given key.
    """
    for key, value in options:
        if key == search_key:
            return value


def register_default_options(ini, default_options):
    """
    Register set of default options.
    """
    for key, value in default_options:
        ini.register(key, value)
    ini.init()
    return ini
