#
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
FrameGroup constants
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
from .group_addresses import AddressesFrameGroup
from .group_associations import AssociationsFrameGroup
from .group_attributes import AttributesFrameGroup
from .group_citations import CitationsFrameGroup
from .group_media import MediaFrameGroup
from .group_names import NamesFrameGroup
from .group_notes import NotesFrameGroup
from .group_ordinances import LDSOrdinancesFrameGroup
from .group_places import (
    EnclosingPlacesFrameGroup,
    EnclosedPlacesFrameGroup,
)
from .group_repositories import RepositoriesFrameGroup
from .group_sources import SourcesFrameGroup
from .group_timeline import TimelineFrameGroup
from .group_urls import UrlsFrameGroup

_ = glocale.translation.sgettext


GRAMPS_GROUPS = {
    "citation": (
        CitationsFrameGroup,
        _("Citation"),
        _("Citations"),
    ),
    "timeline": (
        TimelineFrameGroup,
        _("Timeline Event"),
        _("Timeline Events"),
    ),
    "media": (
        MediaFrameGroup,
        _("Media Item"),
        _("Media Items"),
    ),
    "ldsord": (
        LDSOrdinancesFrameGroup,
        _("Ordinance"),
        _("Ordinances"),
    ),
    "source": (
        SourcesFrameGroup,
        _("Source"),
        _("Sources"),
    ),
    "repository": (
        RepositoriesFrameGroup,
        _("Repository"),
        _("Repositories"),
    ),
    "note": (
        NotesFrameGroup,
        _("Note"),
        _("Notes"),
    ),
    "association": (
        AssociationsFrameGroup,
        _("Association"),
        _("Associations"),
    ),
    "address": (
        AddressesFrameGroup,
        _("Address"),
        _("Addresses"),
    ),
    "attribute": (
        AttributesFrameGroup,
        _("Attribute"),
        _("Attributes"),
    ),
    "enclosing": (
        EnclosingPlacesFrameGroup,
        _("Enclosing Place"),
        _("Enclosing Places"),
    ),
    "enclosed": (
        EnclosedPlacesFrameGroup,
        _("Enclosed Place"),
        _("Enclosed Places"),
    ),
    "name": (
        NamesFrameGroup,
        _("Name"),
        _("Names"),
    ),
    "url": (
        UrlsFrameGroup,
        _("Url"),
        _("Urls"),
    ),
}
