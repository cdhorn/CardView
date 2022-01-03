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
GrampObjectView related constants
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames import (
    AddressFrame,
    AttributeFrame,
    ChildRefFrame,
    CitationFrame,
    EventFrame,
    EventRefFrame,
    FamilyFrame,
    MediaFrame,
    MediaRefFrame,
    NameFrame,
    NoteFrame,
    LDSOrdinanceFrame,
    PersonFrame,
    PersonRefFrame,
    PlaceFrame,
    RepositoryFrame,
    RepositoryRefFrame,
    SourceFrame,
    TagFrame,
)

FRAME_MAP = {
    "Address": AddressFrame,
    "Attribute": AttributeFrame,
    "ChildRef": ChildRefFrame,
    "Citation": CitationFrame,
    "Event": EventFrame,
    "EventRef": EventRefFrame,
    "Family": FamilyFrame,
    "LdsOrd": LDSOrdinanceFrame,
    "Media": MediaFrame,
    "MediaRef": MediaRefFrame,
    "Name": NameFrame,
    "Note": NoteFrame,
    "Person": PersonFrame,
    "PersonRef": PersonRefFrame,
    "Place": PlaceFrame,
    "Repository": RepositoryFrame,
    "RepoRef": RepositoryRefFrame,
    "Source": SourceFrame,
    "Tag": TagFrame,
}
