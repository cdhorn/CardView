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
User customizable field factory and builder functions.
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..services.service_fields import FieldCalculatorService
from .field_base import (
    get_attribute_field,
    get_event_field,
    get_fact_field,
    get_relation_field,
)


def field_factory(field_type, field_value):
    """
    A factory to return a user customizable field renderer.
    """
    if field_type == "Attribute":
        render = get_attribute_field
    elif field_type == "Event":
        render = get_event_field
    elif field_type == "Fact":
        render = get_fact_field
    elif field_type == "Relation":
        render = get_relation_field
    elif field_type == "Calculated":
        render = FieldCalculatorService().get_field
    else:
        render = []
    return render


def field_builder(grstate, obj, field_type, field_value, args):
    """
    A builder to generate widgets to render user customizable fields.

    Required args:

      get_label       Method to generate a styled label
      get_link        Method to generate a styled link to an object
      event_cache     Event objects to examine when field_type is
                      "Event" or "Fact"
    """
    if field_value != "None":
        field = field_factory(field_type, field_value)
        if field:
            return field(grstate, obj, field_value, args)
    return []
