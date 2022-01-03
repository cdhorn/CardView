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
SourceAction
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import RepoRef, Repository
from gramps.gui.editors import EditRepoRef, EditRepository, EditSource
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SourceAction class
#
# ------------------------------------------------------------------------
class SourceAction(GrampsAction):
    """
    Class to support actions related to source objects.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(self, grstate, action_object, target_object)
        if self.action_object.obj_type != "Source":
            raise AttributeError(
                "action_object is %s not a Source"
                % self.action_object.obj_type
            )

    def edit_source(self, *_dummy_args):
        """
        Edit the source.
        """
        try:
            EditSource(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
            )
        except WindowActiveError:
            pass

    def _edit_repository_reference(self, repository, repo_ref, callback):
        """
        Launch the repository reference editor.
        """
        try:
            EditRepoRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                repository,
                repo_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_repository_reference(self, *_dummy_args):
        """
        Launch the editor.
        """
        if self.target_object.obj_type != "RepoRef":
            raise AttributeError(
                "target_object is %s not a RepoRef"
                % self.target_object.obj_type
            )
        repository = self.db.get_repository_from_handle(
            self.target_object.obj.ref
        )
        self._edit_repository_reference(
            repository,
            self.target_object.obj.ref,
            self._edited_repository_reference,
        )

    def _edited_repository_reference(self, repository_tuple):
        """
        Save the repository reference edit.
        """
        if not repository_tuple:
            return
        (dummy_repo_ref, repository) = repository_tuple
        message = self.commit_message(
            _("RepoRef"), repository.get_gramps_id(), action="update"
        )
        self.action_object.commit(self.grstate, message)

    def add_new_repository(self, *_dummy_args):
        """
        Add a new repository.
        """
        repository = Repository()
        try:
            EditRepository(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                repository,
                self.add_new_repository_reference,
            )
        except WindowActiveError:
            pass

    def add_existing_repository(self, *_dummy_args):
        """
        Add an existing repository.
        """
        get_repository_selector = SelectorFactory("Repository")
        skip = [x.ref for x in self.action_object.obj.get_reporef_list()]
        repository_selector = get_repository_selector(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        repository_handle = repository_selector.run()
        if repository_handle:
            self.add_new_repository_reference(repository_handle)

    def add_new_repository_reference(self, obj_or_handle):
        """
        Add new repository reference to source.
        """
        if isinstance(obj_or_handle, str):
            repository_handle = obj_or_handle
            repository = self.db.get_repository_from_handle(repository_handle)
        else:
            repository_handle = obj_or_handle.get_handle()
            repository = obj_or_handle
        for repo_ref in self.action_object.obj.get_reporef_list():
            if repo_ref.ref == repository_handle:
                return
        repo_ref = RepoRef()
        repo_ref.ref = repository_handle
        try:
            EditRepoRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                repository,
                repo_ref,
                self._added_repository_reference,
            )
        except WindowActiveError:
            pass

    def _added_repository_reference(self, repo_tuple):
        """
        Finish adding the repository reference.
        """
        (repo_ref, repository) = repo_tuple
        message = " ".join(
            (
                _("Added"),
                _("RepoRef"),
                repository.get_gramps_id(),
                _("to"),
                _("Source"),
                self.action_object.obj.get_gramps_id(),
            )
        )
        self.action_object.obj.add_repo_reference(repo_ref)
        self.action_object.commit(self.grstate, message)

    def remove_repository_reference(self, *_dummy_args):
        """
        Remove repository reference.
        """
        if self.target_object.obj_type != "RepoRef":
            raise AttributeError(
                "target_object is %s not a RepoRef"
                % self.target_object.obj_type
            )
        repository = self.db.get_repository_from_handle(
            self.target_object.obj.ref
        )
        text = self.describe_object(self.target_object.obj)
        prefix = _(
            "You are about to remove the following repository for this "
            "source:"
        )
        extra = _(
            "Note this does not delete the repository. You can also use "
            "the undo option under edit if you change your mind later."
        )
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            new_list = []
            for repo_ref in self.action_object.obj.get_reporef_list():
                if not repo_ref.ref == self.target_object.obj.ref:
                    new_list.append(repo_ref)
            message = " ".join(
                (
                    _("Removed"),
                    _("RepoRef"),
                    repository.get_gramps_id(),
                    _("from"),
                    _("Source"),
                    self.action_object.obj.get_gramps_id(),
                )
            )
            self.action_object.obj.set_reporef_list(new_list)
            self.action_object.commit(self.grstate, message)
