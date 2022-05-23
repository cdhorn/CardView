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
ProfileManager
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as configman
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug import BasePluginManager
from gramps.gui.pluginmanager import GuiPluginManager

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .config_const import BASE_TEMPLATE_NAME
from .config_defaults import VIEWDEFAULTS
from ..services.service_fields import FieldCalculatorService
from ..services.service_status import StatusIndicatorService

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# ProfileManager Class
#
# -------------------------------------------------------------------------
class ProfileManager:
    """
    Class to manage configuration profiles.
    """

    def __init__(self, dbstate, config):
        self.dbstate = dbstate
        self.config = config
        self.user_options = None
        self.db_options = None

    def _load_active_template(self):
        """
        Load active template configuration options.
        """
        profile_name = self.config.get("templates.active")
        user_ini_file = "_".join(
            (BASE_TEMPLATE_NAME, "template", profile_name)
        )
        self.user_options = load_user_ini_file(user_ini_file)
        if self.dbstate and self.dbstate.db:
            db_ini_file = "_".join((BASE_TEMPLATE_NAME, "database"))
            dbid = self.dbstate.db.get_dbid()
            if dbid:
                db_ini_file = "_".join((db_ini_file, dbid))
                active_options = self.get_active_user_options()
                self.db_options = load_database_ini_file(
                    db_ini_file, active_options
                )

    def get_active_user_options(self):
        """
        Extract active user options.
        """
        options = []
        user_options = self.user_options
        for section in user_options.get_sections():
            for setting in user_options.get_section_settings(section):
                key = ".".join((section, setting))
                value = user_options.get(key)
                options.append((key, value))
        return options

    def get_active_options(self):
        """
        Return configuration manager object.
        """
        self._load_active_template()
        if self.db_options:
            return self.db_options
        return self.user_options


def get_base_template_options(name):
    """
    Get base template options.
    """
    options = VIEWDEFAULTS
    defaults = "Default"
    if name != "Default":
        plugin_manager = BasePluginManager.get_instance()
        plugin_manager.load_plugin_category("TEMPLATE")
        plugin_data = plugin_manager.get_plugin_data("TEMPLATE")
        for plugin in plugin_data:
            if plugin["name"] == name:
                options = plugin["options"]
                defaults = name
                break
    options = merge_defaults(options, StatusIndicatorService().get_defaults())
    options = merge_defaults(options, FieldCalculatorService().get_defaults())
    return options, defaults


def merge_defaults(options, defaults):
    """
    Merge two sets of default values.
    """
    options = list(options)
    for (key, value) in defaults:
        found = False
        for (option_key, option_value) in options:
            if option_key == key:
                found = True
                break
        if not found:
            options = options + [(key, value)]
    return tuple(options)


def get_ini_config_manager(ini_file):
    """
    Return config manager instance for an ini file.
    """
    ini = configman.register_manager(
        ini_file.replace(" ", "_"),
        use_config_path=True,
        use_plugins_path=False,
    )
    ini.register("template.normal_defaults", "")
    ini.register("template.active_defaults", "")
    return ini


def find_option_value(options, search_key):
    """
    Return option value given key.
    """
    for key, value in options:
        if key == search_key:
            return value


def register_default_options(ini, default_options, base=False):
    """
    Register set of default options.
    """
    for key, value in default_options:
        ini.register(key, value)
        if base and key in [
            "template.name_lang_string",
            "template.name_xml_string",
            "template.name_description",
        ]:
            value = find_option_value(
                default_options, key.replace("name_", "base_")
            )
            if value:
                ini.set(key, value)
    ini.init()
    return ini


def load_user_ini_file(ini_file, default_base_name="Default"):
    """
    Load a user ini file.
    """
    ini = get_ini_config_manager(ini_file)
    ini.load()
    set_base = False
    normal_defaults = ini.get("template.normal_defaults")
    if not normal_defaults:
        set_base = True
        normal_defaults = default_base_name
    base_options, choosen_defaults = get_base_template_options(normal_defaults)
    ini = register_default_options(ini, base_options, base=set_base)
    if not ini.get("template.normal_defaults"):
        ini.set("template.normal_defaults", normal_defaults)
    ini.set("template.active_defaults", choosen_defaults)
    ini.save()
    return ini


def load_database_ini_file(ini_file, user_options):
    """
    Load a database ini file.
    """
    ini = get_ini_config_manager(ini_file)
    return register_default_options(ini, user_options)
