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
ProfileManager
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as configman

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..services.service_status import StatusIndicatorService
from ..services.service_fields import FieldCalculatorService


# -------------------------------------------------------------------------
#
# ProfileManager class
#
# -------------------------------------------------------------------------
class ProfileManager:
    """
    Class to manage configuration profiles.
    """

    def __init__(
        self, _dummy_identity, default_options, user_ini, db_ini=None
    ):
        default_options = tuple(
            list(default_options)
            + StatusIndicatorService().get_defaults()
            + FieldCalculatorService().get_defaults()
        )
        self.user_options = load_ini_file(user_ini, default_options)
        if db_ini:
            active_options = self.get_active_options()
            self.db_options = load_ini_file(db_ini, active_options)
        else:
            self.db_options = None

    def get_config_manager(self):
        """
        Return configuration manager object.
        """
        if self.db_options:
            return self.db_options
        return self.user_options

    def get_active_options(self):
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


def load_ini_file(ini_file, default_options):
    """
    Load an ini file.
    """
    ini = configman.register_manager(
        ini_file.replace(" ", "_"),
        use_config_path=True,
        use_plugins_path=False,
    )
    for key, value in default_options:
        ini.register(key, value)
    ini.load()
    ini.save()
    return ini
