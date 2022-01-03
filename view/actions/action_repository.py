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
RepositoryAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import RepoRef
from gramps.gui.editors import EditRepository, EditRepoRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoryAction class
#
# ------------------------------------------------------------------------
class RepositoryAction(GrampsAction):
    """
    Class to support actions on repositories.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)

    def edit_repository(self, *_dummy_args):
        """
        Edit the repository.
        """
        try:
            EditRepository(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
            )
        except WindowActiveError:
            pass

    def add_new_source(self, *_dummy_args):
        """
        Add new repository reference to source.
        """
        if self.target_object.obj_type != "Source":
            raise AttributeError(
                "target_object is %s not a Source"
                % self.target_object.obj_type
            )

        for repo_ref in self.target_object.obj.get_reporef_list():
            if repo_ref.ref == self.action_object.obj.get_handle():
                return
        repo_ref = RepoRef()
        repo_ref.ref = self.action_object.obj.get_handle()
        try:
            EditRepoRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                repo_ref,
                self._added_repository_reference,
            )
        except WindowActiveError:
            pass

    def _added_repository_reference(self, repo_tuple):
        """
        Save updated source.
        """
        (repo_ref, repository) = repo_tuple
        message = " ".join(
            (
                _("Added"),
                _("RepoRef"),
                repository.get_gramps_id(),
                _("to"),
                _("Source"),
                self.target_object.obj.get_gramps_id(),
            )
        )
        self.target_object.obj.add_repo_reference(repo_ref)
        self.target_object.commit(self.grstate, message)


factory.register_action("Repository", RepositoryAction)
