#
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
Group constants
"""

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .group_utils import (
    get_addresses_group,
    get_associations_group,
    get_attributes_group,
    get_children_group,
    get_citations_group,
    get_events_group,
    get_media_group,
    get_names_group,
    get_notes_group,
    get_ordinances_group,
    get_parents_group,
    get_references_group,
    get_repositories_group,
    get_spouses_group,
    get_timeline_group,
    get_urls_group,
)

OBJECT_GROUPS = {
    "address": get_addresses_group,
    "association": get_associations_group,
    "attribute": get_attributes_group,
    "child": get_children_group,
    "citation": get_citations_group,
    "event": get_events_group,
    "media": get_media_group,
    "name": get_names_group,
    "note": get_notes_group,
    "ordinance": get_ordinances_group,
    "parent": get_parents_group,
    "reference": get_references_group,
    "repository": get_repositories_group,
    "spouse": get_spouses_group,
    "timeline": get_timeline_group,
    "url": get_urls_group,
}
