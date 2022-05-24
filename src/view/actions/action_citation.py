#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
CitationAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Citation, Source
from gramps.gui.dialog import WarningDialog
from gramps.gui.editors import EditCitation, EditSource
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..zotero.zotero import GrampsZotero
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CitationAction Class
#
# action_object is the Citation when applicable
# target_object and target_child_object are CitationBase objects
#
# ------------------------------------------------------------------------
class CitationAction(GrampsAction):
    """
    Class to support actions on or with citation objects.
    """

    def __init__(
        self,
        grstate,
        action_object=None,
        target_object=None,
        target_child_object=None,
    ):
        GrampsAction.__init__(
            self, grstate, action_object, target_object, target_child_object
        )
        if self.grstate.config.get("general.zotero-enabled"):
            self.zotero = GrampsZotero(self.db)
        else:
            self.zotero = None

    def _edit_citation(self, focus=False, callback=None):
        """
        Launch the citation editor.
        """
        if focus and callback is None:
            callback = lambda x: self.pivot_focus(x, "Citation")
        source_handle = self.action_object.obj.get_reference_handle()
        if source_handle:
            source = self.db.get_source_from_handle(source_handle)
        else:
            source = Source()
        try:
            EditCitation(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.action_object.obj,
                source,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_citation(self, *_dummy_args, focus=False):
        """
        Edit a citation.
        """
        self._edit_citation(focus=focus)

    def added_citation(self, citation_handle):
        """
        Add the new or existing citation to the current object.
        """
        if citation_handle:
            active_target_object = self.get_target_object()
            citation = self.db.get_citation_from_handle(citation_handle)
            message = _("Added Citation %s to %s %s") % (
                self.describe_object(citation),
                active_target_object.obj_lang,
                self.describe_object(active_target_object.obj),
            )
            active_target_object.save_hash()
            if active_target_object.obj.add_citation(citation_handle):
                active_target_object.sync_hash(self.grstate)
                self.target_object.commit(self.grstate, message)

    def add_new_source_citation(self, *_dummy_args):
        """
        Add a new source from which to create a new citation.
        """
        try:
            EditSource(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                Source(),
                self.add_new_citation,
            )
        except WindowActiveError:
            pass

    def add_existing_source_citation(self, *_dummy_args):
        """
        Select an existing source from which to create a citation.
        """
        get_source_selector = SelectorFactory("Source")
        source_selector = get_source_selector(
            self.grstate.dbstate, self.grstate.uistate
        )
        source_handle = source_selector.run()
        if source_handle:
            self.add_new_citation(source_handle)

    def add_new_citation(self, obj_or_handle):
        """
        Add a new citation.
        """
        if isinstance(obj_or_handle, str):
            source_handle = obj_or_handle
        else:
            source_handle = obj_or_handle.get_handle()
        self.action_object = GrampsObject(Citation())
        self.action_object.obj.set_reference_handle(source_handle)
        self._edit_citation(callback=self.added_citation)

    def add_existing_citation(self, *_dummy_args):
        """
        Add an existing citation.
        """
        get_citation_selector = SelectorFactory("Citation")
        citation_selector = get_citation_selector(
            self.grstate.dbstate, self.grstate.uistate, []
        )
        selection = citation_selector.run()
        if selection:
            if isinstance(selection, Source):
                self.action_object = GrampsObject(Citation())
                self.action_object.obj.set_reference_handle(
                    selection.get_handle()
                )
            elif isinstance(selection, Citation):
                self.action_object = GrampsObject(selection)
            self._edit_citation(callback=self.added_citation)

    def add_zotero_citation(self, *_dummy_args):
        """
        Add citation and possible sources as well using Zotero picker.
        """
        if self.zotero.online:
            import_notes = self.grstate.config.get(
                "general.zotero-enabled-notes"
            )
            active_target_object = self.get_target_object()
            self.zotero.add_citation(
                self.target_object.obj,
                active_target_object.obj,
                import_notes=import_notes,
            )
        else:
            WarningDialog(
                _("Could Not Connect To Local Zotero Client"),
                _(
                    "A connection test to the local Zotero client using "
                    "the Better BibTex Zotero extension failed. The local "
                    "Zotero client needs to be running and extension "
                    "installed in order to use it as a citation picker."
                ),
                parent=self.grstate.uistate.window,
            )

    def remove_citation(self, *_dummy_args):
        """
        Remove the given citation from the current object.
        """
        if not self.action_object:
            return
        active_target_object = self.get_target_object()
        citation_text = self.describe_object(self.action_object.obj)

        message1 = _("Remove Citation %s?") % citation_text
        if active_target_object.is_primary:
            message2 = (
                _(
                    "Removing the citation will remove the citation from the "
                    "%s in the database."
                )
                % active_target_object.obj_lang.lower()
            )
        else:
            message2 = _(
                "Removing the citation will remove the citation from the "
                "%s in the %s in the database."
            ) % (
                active_target_object.obj_lang.lower(),
                self.target_object.obj_lang.lower(),
            )
        self.verify_action(
            message1,
            message2,
            _("Remove Citation"),
            self._remove_citation,
            recover_message=False,
        )

    def _remove_citation(self, *_dummy_args):
        """
        Actually remove the citation.
        """
        active_target_object = self.get_target_object()
        if active_target_object.is_primary:
            message = _("Removed Citation %s from %s %s") % (
                self.describe_object(self.action_object.obj),
                self.target_object.obj_lang,
                self.describe_object(self.target_object.obj),
            )
        else:
            message = _("Removed Citation %s from %s in %s %s") % (
                self.describe_object(self.action_object.obj),
                self.target_child_object.obj_lang,
                self.target_object.obj_lang,
                self.describe_object(self.target_object.obj),
            )
        active_target_object.save_hash()
        active_target_object.obj.remove_citation_references(
            [self.action_object.obj.get_handle()]
        )
        active_target_object.sync_hash(self.grstate)
        self.target_object.commit(self.grstate, message)


factory.register_action("Citation", CitationAction)
