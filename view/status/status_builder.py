# Gramps - a GTK+/GNOME based genealogy program
#
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
Object status factory and builder functions.
"""

# -------------------------------------------------------------------------
#
# Gtk Modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib import Person

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .status_todo import get_todo_status
from .status_person import get_person_status


def status_factory(obj):
    """
    A factory to return a list of status indicator generating functions
    based on object type.
    """
    funcs = []
    if isinstance(obj, Person):
        funcs.append(get_person_status)
    if hasattr(obj, "note_list"):
        funcs.append(get_todo_status)
    #    if hasattr(obj, "attribute_list"):
    #        funcs.append(get_attribute_status)
    return funcs


def status_builder(grstate, obj):
    """
    A builder to return a list of status icons based on object type.
    """
    icon_list = []
    func_list = status_factory(obj)
    if func_list:
        for func in func_list:
            icon_list = icon_list + func(grstate, obj)
    return icon_list
