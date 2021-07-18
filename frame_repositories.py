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
from gramps.gen.db import DbTxn


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_list import GrampsFrameList
from frame_repository import RepositoryGrampsFrame
from frame_utils import get_gramps_object_type

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# RepositoriesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class RepositoriesGrampsFrameGroup(GrampsFrameList):
    """
    The RepositoriesGrampsFrameGroup class provides a container for managing
    all of the repositories that may contain a Source.
    """

    def __init__(self, grstate, obj):
        GrampsFrameList.__init__(self, grstate)
        self.obj = obj
        self.obj_type, discard1, discard2 = get_gramps_object_type(obj)

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }

        repository_list = []
        for repo_ref in obj.get_reporef_list():
            repository = grstate.dbstate.db.get_repository_from_handle(repo_ref.ref)
            repository_list.append((repository, repo_ref))

        if repository_list:
            if self.option("repositories", "sort-by-date"):
                repository_list.sort(key=lambda x: x[0][0].get_date_object().get_sort_value())

            for repository, repo_ref in repository_list:
                frame = RepositoryGrampsFrame(
                    grstate,
                    "repository",
                    repository,
                    repo_ref=repo_ref,
                    groups=groups,
                )
                self.add_frame(frame)
        self.show_all()

    # Todo: Add drag and drop to reorder or add to repo list
    def save_new_object(self, handle, insert_row):
        """
        Add new repository to the list.
        """
        return
