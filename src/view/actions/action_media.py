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
MediaAction
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import os

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Media, MediaRef
from gramps.gen.utils.file import media_path, relative_path
from gramps.gui.editors import EditMedia, EditMediaRef
from gramps.gui.selectors import SelectorFactory

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from .action_base import GrampsAction
from .action_factory import factory

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaAction Class
#
# action_object is the Media or MediaRef when applicable
# target_object is the MediaBase object
#
# ------------------------------------------------------------------------
class MediaAction(GrampsAction):
    """
    Class to support actions related to or for media objects.
    """

    def __init__(self, grstate, action_object=None, target_object=None):
        GrampsAction.__init__(
            self,
            grstate,
            action_object,
            target_object,
        )
        self.filepath = None

    def set_media_file_path(self, filepath):
        """
        Set media file path.
        """
        self.filepath = filepath

    def _edit_media(self, media, callback=None):
        """
        Launch media editor.
        """
        try:
            EditMedia(
                self.grstate.dbstate, self.grstate.uistate, [], media, callback
            )
        except WindowActiveError:
            pass

    def _edit_media_reference(self, media, media_ref, callback=None):
        """
        Launch media reference editor.
        """
        try:
            EditMediaRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                media,
                media_ref,
                callback,
            )
        except WindowActiveError:
            pass

    def edit_media(self, *_dummy_args):
        """
        Edit a media object or reference.
        """
        if self.action_object.obj_type == "Media":
            self._edit_media(self.action_object.obj)
        else:
            media = self.db.get_media_from_handle(self.action_object.obj.ref)
            self._edit_media_reference(
                media, self.action_object.obj, self._edited_media_reference
            )

    def _edited_media_reference(self, media_ref, media):
        """
        Save the edited media reference.
        """
        if not media_ref and media:
            return
        message = _("Edited Media %s for %s %s") % (
            self.describe_object(media),
            self.target_object.obj_lang,
            self.describe_object(self.target_object.obj),
        )
        self.target_object.commit(self.grstate, message)

    def add_new_media(self, *_dummy_args):
        """
        Add a new media item.
        """
        media = Media()
        if self.filepath:
            if self.filepath[:5] != "file:":
                return
            filename = self.filepath[5:]
            while filename[:2] == "//":
                filename = filename[1:]
            if not os.path.isfile(filename):
                return

            if global_config.get("behavior.addmedia-relative-path"):
                base_path = str(media_path(self.db))
                if not os.path.exists(base_path):
                    return
                filename = relative_path(filename, base_path)
            media.set_path(filename)
        self._edit_media(media, self.add_new_media_reference)

    def add_new_media_reference(self, obj_or_handle):
        """
        Add a new media reference.
        """
        if isinstance(obj_or_handle, str):
            media = self.db.get_media_from_handle(obj_or_handle)
        else:
            media = obj_or_handle
        for media_ref in self.target_object.obj.get_media_list():
            if media_ref.ref == media.get_handle():
                return
        ref = MediaRef()
        ref.ref = media.get_handle()
        self._edit_media_reference(media, ref, self._added_new_media_reference)

    def _added_new_media_reference(self, reference, media):
        """
        Finish adding a new media reference.
        """
        message = _("Added Media %s to %s %s") % (
            self.describe_object(media),
            self.target_object.obj_lang,
            self.describe_object(self.target_object.obj),
        )
        self.target_object.obj.add_media_reference(reference)
        self.target_object.commit(self.grstate, message)

    def add_existing_media(self, *_dummy_args):
        """
        Add an existing media item.
        """
        get_media_selector = SelectorFactory("Media")
        media_selector = get_media_selector(
            self.grstate.dbstate, self.grstate.uistate, []
        )
        media = media_selector.run()
        if media:
            self.add_new_media_reference(media.get_handle())

    def remove_media_reference(self, *_dummy_args):
        """
        Remove a media reference.
        """
        if not self.action_object:
            return
        if self.action_object.obj_type == "Media":
            media = self.action_object.obj
        else:
            media = self.db.get_media_from_handle(self.action_object.obj.ref)

        message1 = _("Remove Media %s?") % self.describe_object(media)
        message2 = _(
            "Removing the media will remove the media "
            "reference from the %s %s in the database."
        ) % (
            self.target_object.obj_lang.lower(),
            self.describe_object(self.target_object.obj),
        )
        self.verify_action(
            message1,
            message2,
            _("Remove Media"),
            self._remove_media_reference,
            recover_message=False,
        )

    def _remove_media_reference(self, *_dummy_args):
        """
        Actually remove the media reference.
        """
        if self.action_object.obj_type == "Media":
            media_handle = self.action_object.obj.get_handle()
            media = self.action_object.obj
        else:
            media_handle = self.action_object.obj.ref
            media = self.db.get_media_from_handle(self.action_object.obj.ref)
        message = _("Removed Media %s from %s %s") % (
            self.describe_object(media),
            self.target_object.obj_lang,
            self.describe_object(self.target_object.obj),
        )
        self.target_object.obj.remove_media_references([media_handle])
        self.target_object.commit(self.grstate, message)

    def set_active_media(self, *_dummy_args):
        """
        Make the current media the active media item.
        """
        new_list = []
        image_ref = None
        if self.action_object.obj_type == "Media":
            image_handle = self.action_object.obj.get_handle()
            media = self.action_object.obj
        else:
            image_handle = self.action_object.obj.ref
            media = self.db.get_media_from_handle(image_handle)

        for media_ref in self.target_object.obj.get_media_list():
            if media_ref.ref == image_handle:
                image_ref = media_ref
            else:
                new_list.append(media_ref)
        if image_ref:
            new_list.insert(0, image_ref)

        message = _("Set Media %s Active for %s %s") % (
            self.describe_object(media),
            self.target_object.obj_lang,
            self.describe_object(self.target_object.obj),
        )
        self.target_object.obj.set_media_list(new_list)
        self.target_object.commit(self.grstate, message)

    def delete_object(self, *_dummy_args):
        """
        Delete media object.
        """
        if self.action_object.obj_type == "Media":
            media = self.action_object
        else:
            media = GrampsObject(
                self.db.get_media_from_handle(self.action_object.obj.ref)
            )
        GrampsAction.delete_object(self, None, media)


factory.register_action("Media", MediaAction)
