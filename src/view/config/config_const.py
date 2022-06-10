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
Configuration related constants
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Citation

_ = glocale.translation.sgettext

HELP_VIEW = "https://www.gramps-project.org/wiki/index.php/Addon:CardView"
HELP_CONFIG = "%s%s" % (HELP_VIEW, "_Configuration:")
HELP_CONFIG_TEMPLATES = "%s%s" % (HELP_CONFIG, "Templates")
HELP_CONFIG_DISPLAY = "%s%s" % (HELP_CONFIG, "Global#Display")
HELP_CONFIG_GENERAL = "%s%s" % (HELP_CONFIG, "Global#General")
HELP_CONFIG_MENU = "%s%s" % (HELP_CONFIG, "Global#Context_Menu")
HELP_CONFIG_INDICATORS_BASIC = "%s%s" % (
    HELP_CONFIG,
    "Global#Basic_Indicators",
)
HELP_CONFIG_INDICATORS_STATUS = "%s%s" % (
    HELP_CONFIG,
    "Global#Status_Indicators",
)
HELP_CONFIG_CALCULATED_FIELDS = "%s%s" % (
    HELP_CONFIG,
    "Global#Calculated_Fields",
)
HELP_CONFIG_MEDIA_BAR = "%s%s" % (HELP_CONFIG, "Global#Media_Bar")
HELP_CONFIG_PAGE_LAYOUT = "%s%s" % (HELP_CONFIG, "Layout")
HELP_CONFIG_ACTIVE_OBJECT = "%s%s" % (HELP_CONFIG, "Active")
HELP_CONFIG_OBJECT_GROUPS = "%s%s" % (HELP_CONFIG, "Groups")
HELP_CONFIG_TIMELINES = "%s%s" % (HELP_CONFIG, "Timelines")
HELP_CONFIG_COLORS = "%s%s" % (HELP_CONFIG, "Colors")

BASE_TEMPLATE_NAME = "CardView"

OPTION_VALUE_BIRTH = "Event:Birth"
OPTION_VALUE_BAPTISM = "Event:Baptism"
OPTION_VALUE_CHRISTENING = "Event:Christening"
OPTION_VALUE_WILL = "Event:Will"
OPTION_VALUE_DEATH = "Event:Death"
OPTION_VALUE_BURIAL = "Event:Burial"
OPTION_VALUE_CREMATION = "Event:Cremation"
OPTION_VALUE_PROBATE = "Event:Probate"
OPTION_VALUE_BANNS = "Event:Marriage Banns"
OPTION_VALUE_LICENSE = "Event:Marriage License"
OPTION_VALUE_CONTRACT = "Event:Marriage Contract"
OPTION_VALUE_SETTLEMENT = "Event:Marriage Settlement"
OPTION_VALUE_MARRIAGE = "Event:Marriage"
OPTION_VALUE_FILING = "Event:Divorce Filing"
OPTION_VALUE_DIVORCE = "Event:Divorce"
OPTION_VALUE_ANNULMENT = "Event:Annulment"
OPTION_VALUE_DURATION = "Calculated:Duration"
OPTION_VALUE_RELATIONSHIP = "Calculated:Relationship"
OPTION_VALUE_OCCUPATIONS = "Calculated: Occupations"
OPTION_VALUE_PATERNAL = "Calculated:Paternal Progenitors"
OPTION_VALUE_MATERNAL = "Calculated:Maternal Progenitors"
OPTION_VALUE_BRIDE = "Calculated:Bride Age"
OPTION_VALUE_GROOM = "Calculated:Groom Age"
OPTION_VALUE_CHILD = "Calculated:Child Number"

NOT_DISPLAYED = _("Not displayed")

CONFIDENCE_LEVEL = [
    (Citation.CONF_VERY_LOW, _("Very Low")),
    (Citation.CONF_LOW, _("Low")),
    (Citation.CONF_NORMAL, _("Normal")),
    (Citation.CONF_HIGH, _("High")),
    (Citation.CONF_VERY_HIGH, _("Very High")),
]

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
    (0, NOT_DISPLAYED),
    (1, _("Small image on right")),
    (2, _("Large image on right")),
    (3, _("Small image on left")),
    (4, _("Large image on left")),
]

MEDIA_DISPLAY_MODES = [
    (0, NOT_DISPLAYED),
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
    (0, NOT_DISPLAYED),
    (1, _("Only show state if private")),
    (2, _("Only show state if public")),
    (3, _("Always show state")),
]

SEX_DISPLAY_MODES = [
    (0, NOT_DISPLAYED),
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
    (0, NOT_DISPLAYED),
    (1, _("Display on left")),
    (2, _("Display on top")),
    (3, _("Display on right")),
    (4, _("Display on bottom")),
]

LINEAGE_DISPLAY_MODES = [
    (0, _("Compact")),
    (1, _("Horizontally")),
    (2, _("Vertically")),
]

CATEGORIES = {
    "Person": "People",
    "Relationship": "Relationships",
    "Family": "Families",
    "Event": "Events",
    "Place": "Places",
    "Source": "Sources",
    "Citation": "Citations",
    "Repository": "Repositories",
    "Media": "Media",
    "Note": "Notes",
    "Tag": "Tags",
}

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

PAGE_NAMES = {
    "Address": _("Address"),
    "ChildRef": _("Child Reference"),
    "Citation": _("Citation"),
    "Event": _("Event"),
    "EventRef": _("Event Reference"),
    "Family": _("Family"),
    "LdsOrd": _("LDS Ordinance"),
    "Media": _("Media"),
    "MediaRef": _("Media Reference"),
    "Name": _("Name"),
    "Note": _("Note"),
    "Person": _("Person"),
    "PersonRef": _("Person Reference"),
    "Place": _("Place"),
    "Repository": _("Repository"),
    "RepoRef": _("Repository Reference"),
    "Source": _("Source"),
    "Tag": _("Tag"),
}
