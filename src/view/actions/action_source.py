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
SourceAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import RepoRef, Repository
from gramps.gui.editors import EditRepoRef, EditRepository, EditSource
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SourceAction Class
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

    def edit_source(self, *_dummy_args, focus=False, callback=None):
        """
        Edit the source.
        """
        if focus and callback is None:
            callback = lambda x: self.pivot_focus(x, "Source")
        try:
            EditSource(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                callback,
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
            self.target_object.obj,
            self._edited_repository_reference,
        )

    def _edited_repository_reference(self, repository_tuple):
        """
        Save the repository reference edit.
        """
        if not repository_tuple:
            return
        (dummy_repo_ref, repository) = repository_tuple
        message = _("Edited Repository %s for Source %s") % (
            self.describe_object(repository),
            self.describe_object(self.action_object.obj),
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
        elif isinstance(obj_or_handle, Repository):
            repository_handle = obj_or_handle.get_handle()
            repository = obj_or_handle
        else:
            repository_handle = None
            repository = Repository()
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
        repo_ref.ref = repository.get_handle()
        message = _("Added Repository %s to Source %s") % (
            self.describe_object(repository),
            self.describe_object(self.action_object.obj),
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
        repository_name = self.describe_object(repository)
        source_name = self.describe_object(self.action_object.obj)
        message1 = _("Remove Repository %s?") % repository_name
        message2 = (
            _(
                "Removing the repository will remove the repository "
                "reference from the source %s in the database."
            )
            % source_name
        )
        self.verify_action(
            message1,
            message2,
            _("Remove Repository"),
            self._remove_repository_reference,
            recover_message=False,
        )

    def _remove_repository_reference(self, *_dummy_args):
        """
        Actually remove the repository reference.
        """
        new_list = []
        for repo_ref in self.action_object.obj.get_reporef_list():
            if not repo_ref.ref == self.target_object.obj.ref:
                new_list.append(repo_ref)
        repository = self.db.get_repository_from_handle(
            self.target_object.obj.ref
        )
        message = _("Removed Repository %s from Source %s") % (
            self.describe_object(repository),
            self.describe_object(self.action_object.obj),
        )
        self.action_object.obj.set_reporef_list(new_list)
        self.action_object.commit(self.grstate, message)


factory.register_action("Source", SourceAction)
