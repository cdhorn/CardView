#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
GrampsActionFactory
"""

# ------------------------------------------------------------------------
#
# GrampsActionFactory class
#
# ------------------------------------------------------------------------
class GrampsActionFactory:
    """
    Base class to support actions on or between Gramps objects.
    """

    def __init__(self):
        self._actions = {}

    def register_action(self, obj_type, handler):
        """
        Register action handler.
        """
        self._actions[obj_type] = handler

    def create(self, obj_type, *args):
        """
        Get an action handler.
        """
        handler = self._actions.get(obj_type)
        return handler(*args)


factory = GrampsActionFactory()


def action_handler(*args):
    """
    Return the proper action handler.
    """
    return factory.create(*args)
