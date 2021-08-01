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
MediaGrampsFrameGroup
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
from gramps.gen.db import DbTxn


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..frames.frame_image import ImageGrampsFrame
from ..frames.frame_utils import get_gramps_object_type
from .group_list import GrampsFrameGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class MediaGrampsFrameGroup(GrampsFrameGroupList):
    """
    The MediaGrampsFrameGroup class provides a container for managing all
    of the media items for a given primary Gramps object.
    """

    def __init__(self, grstate, obj):
        GrampsFrameGroupList.__init__(self, grstate)
        self.obj = obj
        self.obj_type, dummy_var1, dummy_var2 = get_gramps_object_type(obj)
        if not self.option("layout", "tabbed"):
            self.hideable = self.option("layout.media", "hideable")

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        media_list = self.collect_media()

        if media_list:
            if self.option("media", "sort-by-date"):
                media_list.sort(
                    key=lambda x: x[0].get_date_object().get_sort_value()
                )

            for (
                media,
                dummy_references,
                dummy_ref_type,
                dummy_ref_desc,
            ) in media_list:
                frame = ImageGrampsFrame(
                    grstate,
                    "media",
                    media,
                    groups=groups,
                )
                self.add_frame(frame)
        self.show_all()

    # Revisit probably needs to be media ref not media
    def save_new_object(self, handle, insert_row):
        """
        Add new media to the list.
        """
        media = self.grstate.dbstate.db.get_media_from_handle()
        action = "{} {} {} {}".format(
            _("Added Media"),
            media.get_gramps_id(),
            _("to"),
            self.obj.get_gramps_id(),
        )
        commit_method = self.grstate.dbstate.db.method(
            "commit_%s", self.obj_type
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            if self.obj.add_media(handle):
                commit_method(self.obj, trans)

    def collect_media(self):
        """
        Helper to collect the media for the current object.
        """
        media_list = []
        self.extract_media(0, self.obj_type, media_list, None, [self.obj])
        return media_list

    def extract_media(
        self, ref_type, ref_desc, media_list, query_method=None, obj_list=None
    ):
        """
        Helper to extract a set of media references from an object.
        """
        if query_method:
            data = query_method()
        else:
            data = obj_list or []
        for item in data:
            if hasattr(item, "media_list"):
                for media_ref in item.get_media_list():
                    media = self.grstate.dbstate.db.get_media_from_handle(
                        media_ref.ref
                    )
                    media_list.append((media, [item], ref_type, ref_desc))
