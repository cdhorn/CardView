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
Page related constants
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale


_ = glocale.translation.sgettext


EVENT_DISPLAY_MODES = [
    (0, _("Show life span only and nothing else")),
    (1, _("Single line with place")),
    (2, _("Single line with no place")),
    (3, _("Abbreviated single line with place")),
    (4, _("Abbreviated single line with no place")),
    (5, _("Split line")),
    (6, _("Abbreviated split line")),
]

IMAGE_DISPLAY_MODES = [
    (0, _("No image displayed")),
    (1, _("Small image on right")),
    (2, _("Large image on right")),
    (3, _("Small image on left")),
    (4, _("Large image on left")),
]

MEDIA_IMAGE_DISPLAY_MODES = [
    (0, _("Not displayed")),
    (1, _("Small full images")),
    (2, _("Small cropped images when available")),
    (3, _("Large full images")),
    (4, _("Large cropped images when available")),
]

PRIVACY_DISPLAY_MODES = [
    (0, _("No indicator displayed")),
    (1, _("Only show state if private")),
    (2, _("Only show state if public")),
    (3, _("Always show state")),
]

SEX_DISPLAY_MODES = [
    (0, _("No indicator displayed")),
    (1, _("Indicator to left of name")),
    (2, _("Indicator to right of name")),
]

TAG_DISPLAY_MODES = [
    (0, _("Disabled")),
    (1, _("Show icons")),
    (2, _("Show tag names")),
    (3, _("Show tag names with color")),
]

TIMELINE_COLOR_MODES = [
    (0, _("Person scheme")),
    (1, _("Relationship scheme")),
    (2, _("Event role scheme")),
    (3, _("Event category scheme")),
    (4, _("Evidence confidence scheme")),
]

# For layout editor
LABELS = {
    "address": _("Addresses"),
    "association": _("Associations"),
    "attribute": _("Attributes"),
    "child": _("Children"),
    "citation": _("Citations"),
    "event": _("Events"),
    "family": _("Families"),
    "media": _("Media"),
    "name": _("Names"),
    "note": _("Notes"),
    "parent": _("Parents"),
    "people": _("People"),
    "person": _("People"),
    "place": _("Places"),
    "reference": _("References"),
    "repository": _("Repositories"),
    "spouse": _("Spouses"),
    "timeline": _("Timeline"),
    "source": _("Sources"),
    "url": _("Urls"),
}

# For layout editor
PAGES = [
    ("Address", _("Address")),
    ("ChildRef", _("ChildRef")),
    ("Citation", _("Citation")),
    ("Event", _("Event")),
    ("Family", _("Family")),
    ("Media", _("Media")),
    ("Name", _("Name")),
    ("Note", _("Note")),
    ("Person", _("Person")),
    ("PersonRef", _("PersonRef")),
    ("Place", _("Place")),
    ("Repository", _("Repository")),
    ("RepoRef", _("RepoRef")),
    ("Source", _("Source")),
    ("Tag", _("Tag")),
]
