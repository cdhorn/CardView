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
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import RepoRef
from gramps.gui.ddtargets import DdTargets
from gramps.gui.editors import EditRepoRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import TextLink
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

        title = TextLink(
            source.title,
            "Source",
            source.get_handle(),
            self.switch_object,
            bold=True,
        )
        self.widgets["title"].pack_start(title, True, False, 0)

        if source.get_author():
            self.add_fact(self.make_label(source.get_author()))

        if source.get_publication_info():
            self.add_fact(self.make_label(source.get_publication_info()))

        if source.get_abbreviation():
            self.add_fact(self.make_label(source.get_abbreviation()))

        self.enable_drag()
        self.dnd_drop_targets.append(DdTargets.REPO_LINK.target())
        self.enable_drop()
        self.set_css_style()

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        if DdTargets.REPO_LINK.drag_type == dnd_type:
            self.add_new_repository(obj_or_handle)
        else:
            self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def add_new_repository(self, obj_or_handle):
        """
        Add new repository reference to source.
        """
        for repo_ref in self.primary.obj.get_reporef_list():
            if repo_ref.ref == obj_or_handle:
                return
        repo_ref = RepoRef()
        repo_ref.ref = obj_or_handle
        repository = self.fetch("Repository", obj_or_handle)
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
