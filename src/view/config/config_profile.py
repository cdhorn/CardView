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
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..services.service_templates import TemplatesService

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
        self.templates_service = TemplatesService(dbstate)
        self.dbstate = dbstate
        self.config = config
        self.user_options = None
        self.db_options = None

    def _load_active_template(self):
        """
        Load active template configuration options.
        """
        profile_name = self.config.get("templates.active")
        (
            active_name,
            self.user_options,
        ) = self.templates_service.get_rebased_user_options(profile_name)
        if active_name != profile_name:
            self.config.set("templates.active", active_name)
            self.config.save()
        if self.dbstate.is_open():
            active_options = self.get_active_user_options()
            self.db_options = (
                self.templates_service.get_rebased_database_options(
                    active_options
                )
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
