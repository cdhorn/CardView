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
SourceGrampsFrame.
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
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import RepoRef, Repository
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditRepoRef, EditRepository
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import menu_item, submenu_item
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# SourceGrampsFrame Class
#
# ------------------------------------------------------------------------
class SourceGrampsFrame(PrimaryGrampsFrame):
    """
    The SourceGrampsFrame exposes some of the basic facts about a Source.
    """

    def __init__(self, grstate, groptions, source):
        PrimaryGrampsFrame.__init__(self, grstate, groptions, source)

        title = self.get_link(
            source.title,
            "Source",
            source.get_handle(),
        )
        self.widgets["title"].pack_start(title, True, False, 0)

        if source.get_author():
            self.add_fact(self.get_label(source.get_author()))

        if source.get_publication_info():
            self.add_fact(self.get_label(source.get_publication_info()))

        if source.get_abbreviation():
            self.add_fact(self.get_label(source.get_abbreviation()))

        self.enable_drag()
        self.dnd_drop_targets.append(DdTargets.REPO_LINK.target())
        self.enable_drop()
        self.set_css_style()

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.REPO_LINK.drag_type == dnd_type:
            self.add_new_repo_ref(obj_or_handle)
            return True
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def add_custom_actions(self, action_menu):
        """
        Add action menu items for the source.
        """
        action_menu.append(self._repositories_option())

    def _repositories_option(self):
        """
        Build the repositories submenu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "list-add", _("Add a new repository"), self.add_new_repository
            )
        )
        menu.add(
            menu_item(
                "list-add",
                _("Add an existing repository"),
                self.add_existing_repository,
            )
        )
        if len(self.primary.obj.get_reporef_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-repository", _("Remove a repository"), removemenu
                )
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            for repo_ref in self.primary.obj.get_reporef_list():
                repository = self.fetch("Repository", repo_ref.ref)
                repository_name = repository.get_name()
                removemenu.add(
                    menu_item(
                        "list-remove",
                        repository_name,
                        self.remove_repo_ref,
                        repo_ref,
                    )
                )
                menu.add(
                    menu_item(
                        "gramps-repository",
                        repository_name,
                        self.edit_repo_ref,
                        repo_ref,
                    )
                )
        return submenu_item("gramps-repository", _("Repositories"), menu)

    def edit_repo_ref(self, _dummy_obj, repo_ref):
        """
        Launch the editor.
        """
        repository = self.fetch("Repository", repo_ref.ref)
        try:
            EditRepoRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                repository,
                repo_ref,
                self._save_repo_ref_edit,
            )
        except WindowActiveError:
            pass

    def _save_repo_ref_edit(self, repository_tuple):
        """
        Save the repository reference edit.
        """
        if not repository_tuple:
            return
        (dummy_repo_ref, repository) = repository_tuple
        message = self._commit_message(
            _("RepoRef"), repository.get_gramps_id(), action="update"
        )
        self.primary.commit(self.grstate, message)

    def add_new_repository(self, *_dummy_obj):
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
                self.add_new_repo_ref,
            )
        except WindowActiveError:
            pass

    def add_existing_repository(self, *_dummy_obj):
        """
        Add an existing repository.
        """
        select_repository = SelectorFactory("Repository")
        skip = set([x.ref for x in self.primary.obj.get_reporef_list()])
        dialog = select_repository(
            self.grstate.dbstate, self.grstate.uistate, skip=skip
        )
        repository_handle = dialog.run()
        if repository_handle:
            self.add_new_repo_ref(repository_handle)

    def add_new_repo_ref(self, obj_or_handle):
        """
        Add new repository reference to source.
        """
        if isinstance(obj_or_handle, str):
            repository_handle = obj_or_handle
            repository = self.fetch("Repository", repository_handle)
        else:
            repository_handle = obj_or_handle.get_handle()
            repository = obj_or_handle
        for repo_ref in self.primary.obj.get_reporef_list():
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
                self._save_repo_ref,
            )
        except WindowActiveError:
            pass

    def _save_repo_ref(self, repo_tuple):
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
                self.primary.obj.get_gramps_id(),
            )
        )
        self.primary.obj.add_repo_reference(repo_ref)
        self.primary.commit(self.grstate, message)

    def remove_repo_ref(self, _dummy_obj, repo_ref):
        """
        Remove repository reference.
        """
        repository = self.fetch("Repository", repo_ref.ref)
        text = repository.get_name()
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
            for ref in self.primary.obj.get_reporef_list():
                if not ref.ref == repo_ref.ref:
                    new_list.append(ref)
            message = " ".join(
                (
                    _("Removed"),
                    _("RepoRef"),
                    repository.get_gramps_id(),
                    _("from"),
                    _("Source"),
                    self.primary.obj.get_gramps_id(),
                )
            )
            self.primary.obj.set_reporef_list(new_list)
            self.primary.commit(self.grstate, message)
