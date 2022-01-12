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
MediaFrameGroup
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import MediaRef
from gramps.gen.lib.mediabase import MediaBase
from gramps.gui.editors import EditMediaRef

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames import MediaRefFrame
from .group_list import FrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaFrameGroup class
#
# ------------------------------------------------------------------------
class MediaFrameGroup(FrameGroupList):
    """
    The MediaFrameGroup class provides a container for managing all
    of the media items for a given primary Gramps object.
    """

    def __init__(self, grstate, groptions, obj):
        FrameGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=True
        )
        groptions.set_backlink(
            (self.group_base.obj_type, self.group_base.obj.get_handle())
        )
        groptions.set_ref_mode(
            self.grstate.config.get("group.media.reference-mode")
        )

        media_list = self.collect_media()
        if media_list:
            if self.get_option("sort-by-date"):
                media_list.sort(
                    key=lambda x: x[1].get_date_object().get_sort_value()
                )

            if self.get_option("group-by-type"):
                photo_list = []
                stone_list = []
                other_list = []
                for media in media_list:
                    if media[2] == "Photo":
                        photo_list.append(media)
                    elif media[2] in ["Tombstone", "Headstone"]:
                        stone_list.append(media)
                    else:
                        other_list.append(media)
                other_list.sort(key=lambda x: x[2])
                media_list = photo_list + stone_list + other_list

            if self.get_option("filter-non-photos"):
                new_list = []
                for media in media_list:
                    if media[2]:
                        if media[2] in [
                            "Photo",
                            "Tombstone",
                            "Headstone",
                        ]:
                            new_list.append(media)
                    else:
                        new_list.append(media)
                media_list = new_list

            maximum = self.grstate.config.get("group.media.max-per-group")
            media_list = media_list[:maximum]
            for (
                media_ref,
                media,
                dummy_media_type,
            ) in media_list:
                frame = MediaRefFrame(
                    grstate, groptions, self.group_base.obj, media_ref
                )
                self.add_frame(frame)
        self.show_all()

    def save_reordered_list(self):
        """
        Save a reordered list of media items.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_media_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
                    break
        message = " ".join(
            (
                _("Reordered"),
                _("Media"),
                _("for"),
                self.group_base.obj_type,
                self.group_base.obj.get_gramps_id(),
            )
        )
        self.group_base.obj.set_media_list(new_list)
        self.group_base.commit(self.grstate, message)

    def save_new_object(self, handle, insert_row):
        """
        Add new media to the list.
        """
        for frame in self.row_frames:
            if frame.primary.obj.get_handle() == handle:
                return

        media_ref = MediaRef()
        media_ref.ref = handle
        media = self.grstate.fetch("Media", handle)
        callback = lambda x, y: self.save_new_media(x, insert_row)
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

    def save_new_media(self, media_ref, insert_row):
        """
        Save the new media reference.
        """
        new_list = []
        for frame in self.row_frames:
            for ref in self.group_base.obj.get_media_list():
                if ref.ref == frame.primary.obj.get_handle():
                    new_list.append(ref)
        new_list.insert(insert_row, media_ref)
        media = self.fetch("Media", media_ref.ref)
        message = " ".join(
            (
                _("Added"),
                _("Media"),
                media.get_gramps_id(),
                _("to"),
                self.group_base.obj_type,
                self.group_base.obj.get_gramps_id(),
            )
        )
        self.group_base.obj.set_media_list(new_list)
        self.group_base.commit(self.grstate, message)

    def collect_media(self):
        """
        Helper to collect the media for the current object.
        """
        media_list = []
        self.extract_media(media_list, self.group_base.obj)
        return media_list

    def extract_media(self, media_list, obj):
        """
        Helper to extract a set of media references from an object.
        """
        if not isinstance(obj, MediaBase):
            return

        for media_ref in obj.get_media_list():
            media = self.fetch("Media", media_ref.ref)
            media_type = ""
            for attribute in media.get_attribute_list():
                if attribute.get_type().xml_str() == "Media-Type":
                    media_type = attribute.get_value()
            media_list.append((media_ref, media, media_type))
