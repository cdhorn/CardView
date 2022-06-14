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
from .group_sources import SourcesCardGroup
from .group_timeline import TimelineCardGroup
from .group_urls import UrlsCardGroup

_ = glocale.translation.sgettext


GENERIC_GROUPS = {
    "citation": (
        CitationsCardGroup,
        _("Citation"),
        _("Citations"),
    ),
    "timeline": (
        TimelineCardGroup,
        _("Timeline Event"),
        _("Timeline Events"),
    ),
    "media": (
        MediaCardGroup,
        _("Media Item"),
        _("Media Items"),
    ),
    "ldsord": (
        LDSOrdinancesCardGroup,
        _("Ordinance"),
        _("Ordinances"),
    ),
    "source": (
        SourcesCardGroup,
        _("Source"),
        _("Sources"),
    ),
    "repository": (
        RepositoriesCardGroup,
        _("Repository"),
        _("Repositories"),
    ),
    "note": (
        NotesCardGroup,
        _("Note"),
        _("Notes"),
    ),
    "association": (
        AssociationsCardGroup,
        _("Association"),
        _("Associations"),
    ),
    "address": (
        AddressesCardGroup,
        _("Address"),
        _("Addresses"),
    ),
    "attribute": (
        AttributesCardGroup,
        _("Attribute"),
        _("Attributes"),
    ),
    "enclosing": (
        EnclosingPlacesCardGroup,
        _("Enclosing Place"),
        _("Enclosing Places"),
    ),
    "enclosed": (
        EnclosedPlacesCardGroup,
        _("Enclosed Place"),
        _("Enclosed Places"),
    ),
    "name": (
        NamesCardGroup,
        _("Name"),
        _("Names"),
    ),
    "url": (
        UrlsCardGroup,
        _("Url"),
        _("Urls"),
    ),
    "paternal": (
        PaternalLineageCardGroup,
        _("Paternal Lineage"),
        _("Paternal Lineage"),
    ),
    "maternal": (
        MaternalLineageCardGroup,
        _("Maternal Lineage"),
        _("Maternal Lineage"),
    ),
}


STATISTICS_GROUPS = {
    "stats-person": _("Individual Statistics"),
    "stats-family": _("Family Statistics"),
    "stats-event": _("Event Statistics"),
    "stats-media": _("Media Statistics"),
    "stats-source": _("Source Statistics"),
    "stats-citation": _("Citation Statistics"),
    "stats-quality": _("Quality Statistics"),
    "stats-privacy": _("Privacy Statistics"),
}
