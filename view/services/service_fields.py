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
FieldCalculatorService
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.plug import BasePluginManager
from gramps.gui.pluginmanager import GuiPluginManager


# -------------------------------------------------------------------------
#
# FieldCalculatorService Class
#
# -------------------------------------------------------------------------
class FieldCalculatorService:
    """
    A singleton class that provides the field calculator service.
    """

    def __new__(cls):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(FieldCalculatorService, cls).__new__(cls)
            cls.instance.__init_singleton__()
        return cls.instance

    def __init_singleton__(self):
        """
        Prepare the field calculator service for use.
        """
        self.field_types = {}
        self.field_generators = {}
        self.default_options = []
        self.config_grid_builders = []
        plugin_manager = GuiPluginManager.get_instance()
        plugin_manager.connect(
            "plugins-reloaded", self.cb_reload_field_plugins
        )
        self.load_field_plugins()

    def cb_reload_field_plugins(self, *args):
        """
        Reload the status plugins if plugin manager was reloaded.
        """
        self.load_field_plugins()

    def load_field_plugins(self):
        """
        Load the status plugins.
        """
        plugin_manager = BasePluginManager.get_instance()
        plugin_manager.load_plugin_category("FIELD")
        plugin_data = plugin_manager.get_plugin_data("FIELD")
        self.field_types.clear()
        self.field_generators.clear()
        self.default_options.clear()
        self.config_grid_builders.clear()
        for plugin in plugin_data:
            supported_types = plugin["supported_types"]
            default_options = plugin["default_options"]
            get_config_grids = plugin["get_config_grids"]
            get_field = plugin["get_field"]
            for supported_type in supported_types:
                if supported_type not in self.field_types:
                    self.field_types[supported_type] = {}
                if supported_type not in self.field_generators:
                    self.field_generators[supported_type] = []
                for (value, value_lang) in supported_types[supported_type]:
                    self.field_types[supported_type].update(
                        {value: value_lang}
                    )
                    key = "%s-%s" % (supported_type, value)
                    self.field_generators[key] = get_field
            if default_options:
                if isinstance(default_options, list):
                    self.default_options = (
                        self.default_options + default_options
                    )
                else:
                    self.default_options.append(default_options)
            if get_config_grids:
                self.config_grid_builders.append(get_config_grids)

    def get_values(self, obj_type):
        """
        Return list of loaded calculated field values based on object type.
        """
        if obj_type in self.field_types:
            return self.field_types[obj_type]
        return {}

    def get_field(self, grstate, obj, field_value, args):
        """
        Generate and return field for an object.
        """
        key = "%s-%s" % (type(obj).__name__, field_value)
        if key in self.field_generators:
            return self.field_generators[key](grstate, obj, field_value, args)
        return []

    def get_defaults(self):
        """
        Return the default field options.
        """
        return self.default_options

    def get_config_grids(self, configdialog, grstate):
        """
        Build and return the configuration dialog grids for the field options.
        """
        grids = []
        for get_config_grid in self.config_grid_builders:
            grid = get_config_grid(configdialog, grstate)
            if isinstance(grid, list):
                grids = grids + grid
            else:
                grids.append(grid)
        return grids
