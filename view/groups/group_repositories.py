#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
RepositoriesGrampsFrameGroup
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


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
from ..frames.frame_repository import RepositoryGrampsFrame
from ..frames.frame_utils import get_gramps_object_type
from .group_list import GrampsFrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoriesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class RepositoriesGrampsFrameGroup(GrampsFrameGroupList):
    """
    The RepositoriesGrampsFrameGroup class provides a container for managing
    all of the repositories that may contain a Source.
    """

    def __init__(self, grstate, groptions, obj):
        GrampsFrameGroupList.__init__(self, grstate, groptions)
        self.obj = obj
        self.obj_type, dummy_var1, dummy_var2 = get_gramps_object_type(obj)
        if not self.get_layout("tabbed"):
            self.hideable = self.get_layout("hideable")

        repository_list = []
        for repo_ref in obj.get_reporef_list():
            repository = grstate.dbstate.db.get_repository_from_handle(
                repo_ref.ref
            )
            repository_list.append((repository, repo_ref))

        if repository_list:
            if self.get_option("sort-by-date"):
                repository_list.sort(
                    key=lambda x: x[0][0].get_date_object().get_sort_value()
                )

            for repository, repo_ref in repository_list:
                frame = RepositoryGrampsFrame(
                    grstate,
                    groptions,
                    repository,
                    repo_ref,
                )
                self.add_frame(frame)
        self.show_all()

    # Todo: Add drag and drop to reorder or add to repo list
    def save_new_object(self, handle, insert_row):
        """
        Add new repository to the list.
        """
        return
