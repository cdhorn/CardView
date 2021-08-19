#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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
Frame constants
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import (
    Address,
    Attribute,
    ChildRef,
    Citation,
    Event,
    Family,
    Media,
    MediaRef,
    Name,
    Note,
    Person,
    PersonRef,
    Place,
    Repository,
    RepoRef,
    Source,
    SrcAttribute,
    Tag,
    Url,
)
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import (
    EditAddress,
    EditAttribute,
    EditChildRef,
    EditCitation,
    EditEvent,
    EditFamily,
    EditMedia,
    EditMediaRef,
    EditName,
    EditNote,
    EditPerson,
    EditPersonRef,
    EditPlace,
    EditRepository,
    EditRepoRef,
    EditSource,
    EditUrl,
)
from gramps.gui.views.tags import EditTag


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
_ = glocale.translation.sgettext


_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3
_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_SPACE = Gdk.keyval_from_name("space")

_GENDERS = {
    Person.MALE: "\u2642",
    Person.FEMALE: "\u2640",
    Person.UNKNOWN: "\u2650",
}

_BIRTH_EQUIVALENTS = ["Baptism", "Christening"]

_DEATH_EQUIVALENTS = ["Burial", "Cremation", "Probate"]

_CONFIDENCE = {
    Citation.CONF_VERY_LOW: _("Very Low"),
    Citation.CONF_LOW: _("Low"),
    Citation.CONF_NORMAL: _("Normal"),
    Citation.CONF_HIGH: _("High"),
    Citation.CONF_VERY_HIGH: _("Very High"),
}

CITATION_TYPES = {0: _("Direct"), 1: _("Indirect")}

CONFIDENCE_COLOR_SCHEME = {
    Citation.CONF_VERY_LOW: "very-low",
    Citation.CONF_LOW: "low",
    Citation.CONF_NORMAL: "normal",
    Citation.CONF_HIGH: "high",
    Citation.CONF_VERY_HIGH: "very-high",
}

EVENT_DISPLAY_MODES = [
    (0, _("Show life span only and nothing else")),
    (1, _("Single line with place")),
    (2, _("Single line with no place")),
    (3, _("Abbreviated single line with place")),
    (4, _("Abbreviated single line with no place")),
    (5, _("Split line")),
    (6, _("Abbreviated split line")),
]

TAG_DISPLAY_MODES = [
    (0, _("Disabled")),
    (1, _("Show icons")),
    (2, _("Show tag names")),
]

IMAGE_DISPLAY_MODES = [
    (0, _("No image displayed")),
    (1, _("Small image on right")),
    (2, _("Large image on right")),
    (3, _("Small image on left")),
    (4, _("Large image on left")),
]

SEX_DISPLAY_MODES = [
    (0, _("No indicator displayed")),
    (1, _("Indicator to left of name")),
    (2, _("Indicator to right of name")),
]

TIMELINE_COLOR_MODES = [
    (0, _("Person scheme")),
    (1, _("Relationship scheme")),
    (2, _("Event category scheme")),
    (3, _("Evidence confidence scheme")),
]

_EDITORS = {
    "Address": EditAddress,
    "Citation": EditCitation,
    "Event": EditEvent,
    "Family": EditFamily,
    "Media": EditMedia,
    "Name": EditName,
    "Note": EditNote,
    "Person": EditPerson,
    "Place": EditPlace,
    "Repository": EditRepository,
    "Source": EditSource,
}

GRAMPS_OBJECTS = [
    (
        Event,
        EditEvent,
        "Event",
        _("Event"),
        DdTargets.EVENT,
        "gramps-event"
    ),
    (
        Citation,
        EditCitation,
        "Citation",
        _("Citation"),
        DdTargets.CITATION_LINK,
        "gramps-citation",
    ),
    (
        Source,
        EditSource,
        "Source",
        _("Source"),
        DdTargets.SOURCE_LINK,
        "gramps-source",
    ),
    (
        Place,
        EditPlace,
        "Place",
        _("Place"),
        DdTargets.PLACE_LINK,
        "gramps-place",
    ),
    (
        Note,
        EditNote,
        "Note",
        _("Note"),
        DdTargets.NOTE_LINK,
        "gramps-notes"
    ),
    (
        Person,
        EditPerson,
        "Person",
        _("Person"),
        DdTargets.PERSON_LINK,
        "gramps-person",
    ),
    (
        Family,
        EditFamily,
        "Family",
        _("Family"),
        DdTargets.FAMILY_LINK,
        "gramps-family",
    ),
    (
        Media,
        EditMedia,
        "Media",
        _("Media"),
        DdTargets.MEDIAOBJ,
        "gramps-media"
    ),
    (
        Repository,
        EditRepository,
        "Repository",
        _("Repository"),
        DdTargets.REPO_LINK,
        "gramps-repository",
    ),
    (
        Address,
        EditAddress,
        "Address",
        _("Address"),
        DdTargets.ADDRESS,
        "gramps-address",
    ),
    (
        Attribute,
        EditAttribute,
        "Attribute",
        _("Attribute"),
        DdTargets.ATTRIBUTE,
        "gramps-attribute",
    ),
    (
        SrcAttribute,
        EditAttribute,
        "Attribute",
        _("Attribute"),
        DdTargets.SRCATTRIBUTE,
        "gramps-attribute",
    ),
    (
        Name,
        EditName,
        "Name",
        _("Name"),
        DdTargets.NAME,
        "gramps-person"
    ),
    (
        Url,
        EditUrl,
        "Url",
        _("Url"),
        DdTargets.URL,
        "gramps-url",
    ),
    (
        ChildRef,
        EditChildRef,
        "ChildRef",
        _("ChildRef"),
        DdTargets.CHILDREF,
        "stock_link",
    ),
    (
        PersonRef,
        EditPersonRef,
        "PersonRef",
        _("PersonRef"),
        DdTargets.PERSONREF,
        "stock_link",
    ),
    (
        RepoRef,
        EditRepoRef,
        "RepoRef",
        _("RepoRef"),
        DdTargets.REPOREF,
        "stock_link",
    ),
    (
        MediaRef,
        EditMediaRef,
        "MediaRef",
        _("MediaRef"),
        DdTargets.MEDIAREF,
        "stock_link",
    ),
    (
        Tag,
        EditTag,
        "Tag",
        _("Tag"),
        None,
        "gramps-tag",
    ),
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
    ("Source", _("Source")),
    ("Tag", _("Tag")),
]
