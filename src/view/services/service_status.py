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
StatusIndicatorService
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
# StatusIndicatorService Class
#
# -------------------------------------------------------------------------
class StatusIndicatorService:
    """
    A singleton class that provides the status indicator service.
    """

    def __new__(cls):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(StatusIndicatorService, cls).__new__(cls)
            cls.instance.__init_singleton__()
        return cls.instance

    def __init_singleton__(self):
        """
        Prepare the status service for use.
        """
        self.status_checks = {}
        self.default_options = []
        self.config_grid_builders = []
        plugin_manager = GuiPluginManager.get_instance()
        plugin_manager.connect(
            "plugins-reloaded", self.cb_reload_status_plugins
        )
        self.load_status_plugins()

    def cb_reload_status_plugins(self, *args):
        """
        Reload the status plugins if plugin manager was reloaded.
        """
        self.load_status_plugins()

    def load_status_plugins(self):
        """
        Load the status plugins.
        """
        plugin_manager = BasePluginManager.get_instance()
        plugin_manager.load_plugin_category("STATUS")
        plugin_data = plugin_manager.get_plugin_data("STATUS")
        self.status_checks.clear()
        self.default_options.clear()
        self.config_grid_builders.clear()
        for plugin in plugin_data:
            supported_types = plugin["supported_types"]
            default_options = plugin["default_options"]
            get_config_grids = plugin["get_config_grids"]
            get_status = plugin["get_status"]
            for supported_type in supported_types:
                if supported_type in self.status_checks:
                    self.status_checks[supported_type].append(get_status)
                else:
                    self.status_checks.update({supported_type: [get_status]})
            if default_options:
                if isinstance(default_options, list):
                    self.default_options = (
                        self.default_options + default_options
                    )
                else:
                    self.default_options.append(default_options)
            if get_config_grids:
                self.config_grid_builders.append(get_config_grids)

    def get_status(self, grstate, obj, size):
        """
        Perform and return status checks for an object.
        """
        results = []
        obj_type = type(obj).__name__
        if obj_type in self.status_checks:
            for status_check in self.status_checks[obj_type]:
                status = status_check(grstate, obj, size)
                if status:
                    results = results + status
        return results

    def get_defaults(self):
        """
        Return the default status options.
        """
        return self.default_options

    def get_config_grids(self, configdialog, grstate):
        """
        Build and return the configuration dialog grids for the status options.
        """
        grids = []
        for get_config_grid in self.config_grid_builders:
            grid = get_config_grid(configdialog, grstate)
            if isinstance(grid, list):
                grids = grids + grid
            else:
                grids.append(grid)
        return grids
