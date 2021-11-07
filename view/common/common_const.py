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
Common constants
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
    EventRef,
    Family,
    LdsOrd,
    Media,
    MediaRef,
    Name,
    Note,
    Person,
    PersonRef,
    Place,
    RepoRef,
    Repository,
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
    EditEventRef,
    EditFamily,
    EditLdsOrd,
    EditMedia,
    EditMediaRef,
    EditName,
    EditNote,
    EditPerson,
    EditPersonRef,
    EditPlace,
    EditRepoRef,
    EditRepository,
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

_MARRIAGE_EQUIVALENTS = ["Marriage License", "Marriage Banns"]

_DIVORCE_EQUIVALENTS = ["Annulment"]

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
        Person,
        EditPerson,
        "Person",
        _("Person"),
        DdTargets.PERSON_LINK,
        "gramps-person",
    ),
    (
        ChildRef,
        EditChildRef,
        "ChildRef",
        _("ChildRef"),
        DdTargets.CHILDREF,
        "stock_link",
    ),
    (Event, EditEvent, "Event", _("Event"), DdTargets.EVENT, "gramps-event"),
    (
        EventRef,
        EditEventRef,
        "EventRef",
        _("EventRef"),
        DdTargets.EVENTREF,
        "gramps-event",
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
        Media,
        EditMedia,
        "Media",
        _("Media"),
        DdTargets.MEDIAOBJ,
        "gramps-media",
    ),
    (
        MediaRef,
        EditMediaRef,
        "MediaRef",
        _("MediaRef"),
        DdTargets.MEDIAREF,
        "stock_link",
    ),
    (Note, EditNote, "Note", _("Note"), DdTargets.NOTE_LINK, "gramps-notes"),
    (
        Family,
        EditFamily,
        "Family",
        _("Family"),
        DdTargets.FAMILY_LINK,
        "gramps-family",
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
    (Name, EditName, "Name", _("Name"), DdTargets.NAME, "gramps-person"),
    (
        Url,
        EditUrl,
        "Url",
        _("Url"),
        DdTargets.URL,
        "gramps-url",
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
        Place,
        EditPlace,
        "Place",
        _("Place"),
        DdTargets.PLACE_LINK,
        "gramps-place",
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
        Repository,
        EditRepository,
        "Repository",
        _("Repository"),
        DdTargets.REPO_LINK,
        "gramps-repository",
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
        Tag,
        EditTag,
        "Tag",
        _("Tag"),
        None,
        "gramps-tag",
    ),
    (
        LdsOrd,
        EditLdsOrd,
        "LdsOrd",
        _("LdsOrd"),
        None,
        "gramps-event",
    ),
]


GROUP_LABELS = {
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
    "ldsord": _("Ordinances"),
    "ordinance": _("Ordinances"),
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
