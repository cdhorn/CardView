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
UrlAction
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Url
from gramps.gui.display import display_url
from gramps.gui.editors import EditUrl

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
# UrlAction Class
#
# action_object is the Url when applicable
# target_object and target_child_object are UrlBase objects
#
# ------------------------------------------------------------------------
class UrlAction(GrampsAction):
    """
    Class to support actions on or with url objects.
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
        self.path = None
        self.description = None

    def set_url(self, url):
        """
        Set the URL object.
        """
        self.set_action_object(url)

    def set_path(self, path):
        """
        Set the URI.
        """
        self.path = path

    def set_description(self, description):
        """
        Set the description.
        """
        self.description = description

    def _edit_url(self, url, callback=None):
        """
        Launch url editor.
        """
        try:
            EditUrl(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                "",
                url,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_url(self, *_dummy_args):
        """
        Edit a url.
        """
        self._edit_url(self.action_object.obj, self._edited_url)

    def _edited_url(self, url):
        """
        Save the edited url.
        """
        if url:
            active_target_object = self.get_target_object()
            message = _("Edited Url %s for %s") % (
                url.path,
                self.describe_object(active_target_object.obj),
            )
            self.target_object.commit(self.grstate, message)

    def add_url(self, *_dummy_args):
        """
        Add a new url.
        """
        url = Url()
        url.set_type("Web Home")
        if self.path:
            url.set_path(self.path)
        if self.description:
            url.set_description(self.description)
        self._edit_url(url, self._added_url)

    def _added_url(self, url):
        """
        Save the new url to finish adding it.
        """
        if url:
            active_target_object = self.get_target_object()
            message = _("Added Url %s to %s") % (
                url.path,
                self.describe_object(active_target_object.obj),
            )
            active_target_object.obj.add_url(url)
            self.target_object.commit(self.grstate, message)

    def delete_object(self, *_dummy_args):
        """
        Delete the given url. This overrides the default method.
        """
        if not self.action_object:
            return
        active_target_object = self.get_target_object()
        target_name = self.describe_object(active_target_object.obj)
        url_name = str(self.action_object.obj.path)
        message1 = _("Delete Url %s?") % url_name
        message2 = _(
            "Deleting the url will remove the url from "
            "the %s %s in the database."
        ) % (active_target_object.obj_lang.lower(), target_name)
        self.verify_action(
            message1,
            message2,
            _("Delete Url"),
            self._delete_object,
        )

    def _delete_object(self, *_dummy_args):
        """
        Actually delete the url.
        """
        active_target_object = self.get_target_object()
        message = _("Deleted Url %s from %s") % (
            self.action_object.obj.path,
            self.describe_object(active_target_object.obj),
        )
        if active_target_object.obj.remove_url(self.action_object.obj):
            self.target_object.commit(self.grstate, message)

    def launch_url(self, *_dummy_args):
        """
        Launch a browser for a url.
        """
        if self.action_object and self.action_object.obj.path:
            display_url(self.action_object.obj.path)

    def edit_object(self, *_dummy_args):
        """
        Edit the url. This overrides default method.
        """
        self.edit_url()


factory.register_action("Url", UrlAction)
