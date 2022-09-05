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
CardGroup constants
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .group_addresses import AddressesCardGroup
from .group_associations import AssociationsCardGroup
from .group_attributes import AttributesCardGroup
from .group_citations import CitationsCardGroup
from .group_lineage import PaternalLineageCardGroup, MaternalLineageCardGroup
from .group_media import MediaCardGroup
from .group_names import NamesCardGroup
from .group_notes import NotesCardGroup
from .group_ordinances import LDSOrdinancesCardGroup
from .group_places import EnclosedPlacesCardGroup, EnclosingPlacesCardGroup
from .group_repositories import RepositoriesCardGroup
from .group_research import ResearchNotesCardGroup
from .group_sources import SourcesCardGroup
from .group_timeline import TimelineCardGroup
from .group_todo import TodoNotesCardGroup
from .group_uncited import UncitedEventsCardGroup
from .group_urls import UrlsCardGroup

_ = glocale.translation.sgettext


GENERIC_GROUPS = {
    "address": (
        AddressesCardGroup,
        _("Address"),
        _("Addresses"),
    ),
    "association": (
        AssociationsCardGroup,
        _("Association"),
        _("Associations"),
    ),
    "attribute": (
        AttributesCardGroup,
        _("Attribute"),
        _("Attributes"),
    ),
    "citation": (
        CitationsCardGroup,
        _("Citation"),
        _("Citations"),
    ),
    "enclosed": (
        EnclosedPlacesCardGroup,
        _("Enclosed Place"),
        _("Enclosed Places"),
    ),
    "enclosing": (
        EnclosingPlacesCardGroup,
        _("Enclosing Place"),
        _("Enclosing Places"),
    ),
    "ldsord": (
        LDSOrdinancesCardGroup,
        _("Ordinance"),
        _("Ordinances"),
    ),
    "maternal": (
        MaternalLineageCardGroup,
        _("Maternal Lineage"),
        _("Maternal Lineage"),
    ),
    "media": (
        MediaCardGroup,
        _("Media Item"),
        _("Media Items"),
    ),
    "name": (
        NamesCardGroup,
        _("Name"),
        _("Names"),
    ),
    "note": (
        NotesCardGroup,
        _("Note"),
        _("Notes"),
    ),
    "paternal": (
        PaternalLineageCardGroup,
        _("Paternal Lineage"),
        _("Paternal Lineage"),
    ),
    "repository": (
        RepositoriesCardGroup,
        _("Repository"),
        _("Repositories"),
    ),
    "research": (
        ResearchNotesCardGroup,
        _("Research Note"),
        _("Research Notes"),
    ),
    "source": (
        SourcesCardGroup,
        _("Source"),
        _("Sources"),
    ),
    "timeline": (
        TimelineCardGroup,
        _("Timeline Event"),
        _("Timeline Events"),
    ),
    "todo": (
        TodoNotesCardGroup,
        _("To Do Note"),
        _("To Do Notes"),
    ),
    "uncited": (
        UncitedEventsCardGroup,
        _("Uncited Event"),
        _("Uncited Events"),
    ),
    "url": (
        UrlsCardGroup,
        _("Url"),
        _("Urls"),
    ),
}


STATISTICS_GROUPS = {
    "stats-association": _("Associations"),
    "stats-bookmark": _("Bookmarks"),
    "stats-child": _("Children"),
    "stats-citation": _("Citations"),
    "stats-event": _("Events"),
    "stats-family": _("Families"),
    "stats-ldsordfamily": _("Family Ordinances"),
    "stats-ldsordperson": _("Person Ordinances"),
    "stats-media": _("Media"),
    "stats-note": _("Notes"),
    "stats-participant": _("Participants"),
    "stats-person": _("People"),
    "stats-place": _("Places"),
    "stats-privacy": _("Privacy"),
    "stats-repository": _("Repositories"),
    "stats-source": _("Sources"),
    "stats-tag": _("Tags"),
    "stats-uncited": _("Uncited Information"),
}
