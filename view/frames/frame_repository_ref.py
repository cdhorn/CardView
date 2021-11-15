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
RepositoryRefGrampsFrame
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
from gramps.gui.editors import EditRepoRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import menu_item
from .frame_repository import RepositoryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoryRefGrampsFrame Class
#
# ------------------------------------------------------------------------
class RepositoryRefGrampsFrame(RepositoryGrampsFrame):
    """
    The RepositoryRefGrampsFrame exposes some of the basic facts about a
    Repository and the reference to it.
    """

    def __init__(self, grstate, groptions, source, repo_ref=None):
        repository = grstate.fetch("Repository", repo_ref.ref)
        RepositoryGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            repository,
            reference_tuple=(source, repo_ref),
        )
        if not groptions.ref_mode:
            return

        vbox = None
        left = groptions.ref_mode == 1
        if self.get_option("show-call-number") and repo_ref.call_number:
            if groptions.ref_mode in [1, 3]:
                self.ref_widgets["body"].pack_start(
                    self.make_label(_("Call number"), left=left),
                    False,
                    False,
                    0,
                )
                self.ref_widgets["body"].pack_start(
                    self.make_label(repo_ref.call_number, left=left),
                    False,
                    False,
                    0,
                )
            else:
                vbox = Gtk.VBox()
                text = "{}: {}".format(
                    _("Call number"), repo_ref.call_number
                ).replace("::", ":")
                vbox.pack_start(self.make_label(text), False, False, 0)

        if self.get_option("show-media-type") and repo_ref.media_type:
            text = glocale.translation.sgettext(repo_ref.media_type.xml_str())
            if groptions.ref_mode in [1, 3]:
                self.ref_widgets["body"].pack_start(
                    self.make_label(
                        "{} {}".format(_("Media"), _("type")), left=left
                    ),
                    False,
                    False,
                    0,
                )
                self.ref_widgets["body"].pack_start(
                    self.make_label(text, left=left), False, False, 0
                )
            else:
                if not vbox:
                    vbox = Gtk.VBox()
                if text:
                    text = "{} {}: {}".format(_("Media"), _("type"), text)
                vbox.pack_start(self.make_label(text), False, False, 0)

            if vbox:
                self.ref_widgets["body"].pack_start(vbox, False, False, 0)

    def add_ref_custom_actions(self, action_menu):
        """
        Build the action menu for a right click on a reference object.
        """
        action_menu.append(self._edit_repo_ref_option())

    def _edit_repo_ref_option(self):
        """
        Build the edit option.
        """
        name = "{} {}".format(_("Edit"), _("reference"))
        return menu_item("gtk-edit", name, self.edit_repo_ref)

    def edit_repo_ref(self, *_dummy_obj):
        """
        Launch the editor.
        """
        try:
            EditRepoRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                self.primary.obj,
                self.reference.obj,
                self.save_ref,
            )
        except WindowActiveError:
            pass
