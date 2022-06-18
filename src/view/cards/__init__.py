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
Module containing the cards for the card groups and page views.
"""

from .card_address import AddressCard
from .card_attribute import AttributeCard
from .card_child_ref import ChildRefCard
from .card_citation import CitationCard
from .card_event import EventCard
from .card_event_ref import EventRefCard
from .card_family import FamilyCard
from .card_family_tree import FamilyTreeCard
from .card_media import MediaCard
from .card_media_ref import MediaRefCard
from .card_name import NameCard
from .card_note import NoteCard
from .card_note_url import NoteUrlCard
from .card_ordinance import LDSOrdinanceCard
from .card_person import PersonCard
from .card_person_backref import PersonBackRefCard
from .card_person_ref import PersonRefCard
from .card_place import PlaceCard
from .card_place_ref import PlaceRefCard
from .card_repository import RepositoryCard
from .card_repository_ref import RepositoryRefCard
from .card_source import SourceCard
from .card_tag import TagCard
from .card_text import TextCard
from .card_url import UrlCard
