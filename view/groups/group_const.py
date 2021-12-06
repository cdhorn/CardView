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
GrampsFrameGroup constants
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
from .group_addresses import AddressesGrampsFrameGroup
from .group_associations import AssociationsGrampsFrameGroup
from .group_attributes import AttributesGrampsFrameGroup
from .group_citations import CitationsGrampsFrameGroup
from .group_media import MediaGrampsFrameGroup
from .group_names import NamesGrampsFrameGroup
from .group_notes import NotesGrampsFrameGroup
from .group_ordinances import LDSOrdinancesGrampsFrameGroup
from .group_repositories import RepositoriesGrampsFrameGroup
from .group_sources import SourcesGrampsFrameGroup
from .group_timeline import TimelineGrampsFrameGroup
from .group_urls import UrlsGrampsFrameGroup

_ = glocale.translation.sgettext


GRAMPS_GROUPS = {
    "citation": (
        CitationsGrampsFrameGroup,
        _("Citation"),
        _("Citations"),
    ),
    "timeline": (
        TimelineGrampsFrameGroup,
        _("Timeline Event"),
        _("Timeline Events"),
    ),
    "media": (
        MediaGrampsFrameGroup,
        _("Media Item"),
        _("Media Items"),
    ),
    "ldsord": (
        LDSOrdinancesGrampsFrameGroup,
        _("Ordinance"),
        _("Ordinances"),
    ),
    "source": (
        SourcesGrampsFrameGroup,
        _("Source"),
        _("Sources"),
    ),
    "repository": (
        RepositoriesGrampsFrameGroup,
        _("Repository"),
        _("Repositories"),
    ),
    "note": (
        NotesGrampsFrameGroup,
        _("Note"),
        _("Notes"),
    ),
    "association": (
        AssociationsGrampsFrameGroup,
        _("Association"),
        _("Associations"),
    ),
    "address": (
        AddressesGrampsFrameGroup,
        _("Address"),
        _("Addresses"),
    ),
    "attribute": (
        AttributesGrampsFrameGroup,
        _("Attribute"),
        _("Attributes"),
    ),
    "name": (
        NamesGrampsFrameGroup,
        _("Name"),
        _("Names"),
    ),
    "url": (
        UrlsGrampsFrameGroup,
        _("Url"),
        _("Urls"),
    ),
}
