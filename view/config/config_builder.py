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
GrampsPageView factory and builder functions
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .config_global import (
    build_display_grid,
    build_general_grid,
    build_indicator_grid,
    build_media_bar_grid,
    build_status_grid,
)
from .config_objects import (
    build_address_grid,
    build_citation_grid,
    build_event_grid,
    build_family_grid,
    build_ldsord_grid,
    build_media_grid,
    build_name_grid,
    build_note_grid,
    build_person_grid,
    build_place_grid,
    build_repository_grid,
    build_source_grid,
)
from .config_panel import build_global_panel
from .config_timeline import (
    build_family_timeline_grid,
    build_person_timeline_grid,
    build_place_timeline_grid,
)

CONFIG_GRID_MAP = {
    "display": build_display_grid,
    "general": build_general_grid,
    "indicator": build_indicator_grid,
    "status": build_status_grid,
    "media-bar": build_media_bar_grid,
    "person": build_person_grid,
    "parent": build_person_grid,
    "sibling": build_person_grid,
    "spouse": build_person_grid,
    "child": build_person_grid,
    "association": build_person_grid,
    "family": build_family_grid,
    "place": build_place_grid,
    "ldsord": build_ldsord_grid,
    "citation": build_citation_grid,
    "source": build_source_grid,
    "repository": build_repository_grid,
    "media": build_media_grid,
    "note": build_note_grid,
    "name": build_name_grid,
    "address": build_address_grid,
    "event": build_event_grid,
}


def config_factory(space, context):
    """
    A factory to return a configuration object.
    """
    if "global" in space:
        func = build_global_panel
    elif "timeline" in space:
        if context == "person":
            func = build_person_timeline_grid
        elif context == "family":
            func = build_family_timeline_grid
        elif context == "place":
            func = build_place_timeline_grid
    else:
        func = CONFIG_GRID_MAP.get(context)
    return func
