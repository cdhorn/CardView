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
RepositoriesCardGroup
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..cards import RepositoryRefCard
from .group_list import CardGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoriesCardGroup Class
#
# ------------------------------------------------------------------------
class RepositoriesCardGroup(CardGroupList):
    """
    The RepositoriesCardGroup class provides a container for managing
    all of the repositories that may contain a Source.
    """

    def __init__(self, grstate, groptions, obj):
        CardGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=False
        )
        groptions.set_ref_mode(
            self.grstate.config.get("group.repository.reference-mode")
        )
        for repo_ref in obj.reporef_list:
            profile = RepositoryRefCard(grstate, groptions, obj, repo_ref)
            self.add_card(profile)
        self.show_all()
