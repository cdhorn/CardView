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
from ..frames.frame_address import AddressGrampsFrame
from ..frames.frame_attribute import AttributeGrampsFrame
from ..frames.frame_child_ref import ChildRefGrampsFrame
from ..frames.frame_citation import CitationGrampsFrame
from ..frames.frame_couple import CoupleGrampsFrame
from ..frames.frame_event import EventGrampsFrame
from ..frames.frame_event_ref import EventRefGrampsFrame
from ..frames.frame_media import MediaGrampsFrame
from ..frames.frame_media_ref import MediaRefGrampsFrame
from ..frames.frame_name import NameGrampsFrame
from ..frames.frame_note import NoteGrampsFrame
from ..frames.frame_ordinance import LDSOrdinanceGrampsFrame
from ..frames.frame_person import PersonGrampsFrame
from ..frames.frame_person_ref import PersonRefGrampsFrame
from ..frames.frame_place import PlaceGrampsFrame
from ..frames.frame_repository import RepositoryGrampsFrame
from ..frames.frame_repository_ref import RepositoryRefGrampsFrame
from ..frames.frame_source import SourceGrampsFrame
from ..frames.frame_tag import TagGrampsFrame


FRAME_MAP = {
    "Address": AddressGrampsFrame,
    "Attribute": AttributeGrampsFrame,
    "ChildRef": ChildRefGrampsFrame,
    "Citation": CitationGrampsFrame,
    "Event": EventGrampsFrame,
    "EventRef": EventRefGrampsFrame,
    "Family": CoupleGrampsFrame,
    "LdsOrd": LDSOrdinanceGrampsFrame,
    "Media": MediaGrampsFrame,
    "MediaRef": MediaRefGrampsFrame,
    "Name": NameGrampsFrame,
    "Note": NoteGrampsFrame,
    "Person": PersonGrampsFrame,
    "PersonRef": PersonRefGrampsFrame,
    "Place": PlaceGrampsFrame,
    "Repository": RepositoryGrampsFrame,
    "RepoRef": RepositoryRefGrampsFrame,
    "Source": SourceGrampsFrame,
    "Tag": TagGrampsFrame,
}
