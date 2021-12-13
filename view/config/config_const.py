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
GrampsPageView related constants
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
    (0, _("Not displayed")),
    (1, _("Small image on right")),
    (2, _("Large image on right")),
    (3, _("Small image on left")),
    (4, _("Large image on left")),
]

MEDIA_DISPLAY_MODES = [
    (0, _("Not displayed")),
    (1, _("Small cropped images")),
    (2, _("Small full images")),
    (3, _("Large cropped images")),
    (4, _("Large full images")),
]

MEDIA_POSITION_MODES = [
    (0, _("Horizontally")),
    (1, _("Left side")),
    (2, _("Right side")),
]

PRIVACY_DISPLAY_MODES = [
    (0, _("Not displayed")),
    (1, _("Only show state if private")),
    (2, _("Only show state if public")),
    (3, _("Always show state")),
]

SEX_DISPLAY_MODES = [
    (0, _("Not displayed")),
    (1, _("Indicator to left of name")),
    (2, _("Indicator to right of name")),
]

TIMELINE_COLOR_MODES = [
    (0, _("Person scheme")),
    (1, _("Event role scheme")),
    (2, _("Event category scheme")),
    (3, _("Evidence confidence scheme")),
    (4, _("Relationship scheme")),
]

EVENT_COLOR_MODES = [
    (0, _("Person scheme")),
    (1, _("Event role scheme")),
    (2, _("Event category scheme")),
    (3, _("Evidence confidence scheme")),
]

REF_DISPLAY_MODES = [
    (0, _("Not displayed")),
    (1, _("Display on left")),
    (2, _("Display on top")),
    (3, _("Display on right")),
    (4, _("Display on bottom")),
]

PAGES = [
    ("Address", _("Address")),
    ("ChildRef", _("ChildRef")),
    ("Citation", _("Citation")),
    ("Event", _("Event")),
    ("EventRef", _("EventRef")),
    ("Family", _("Family")),
    ("LdsOrd", _("LdsOrd")),
    ("Media", _("Media")),
    ("MediaRef", _("MediaRef")),
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
