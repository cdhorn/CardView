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
MediaBar
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
from ..frames.frame_classes import GrampsConfig, GrampsOptions, GrampsImageViewFrame
from ..frames.frame_image import ImageGrampsFrame
from ..frames.frame_utils import get_gramps_object_type

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaBar class
#
# ------------------------------------------------------------------------
class MediaBarGroup(Gtk.ScrolledWindow, GrampsConfig):
    """
    The MediaBarGroup class provides a container for managing a horizontal
    scrollable list of media items for a given primary Gramps object.
    """

    def __init__(self, grstate, groptions, obj):
        Gtk.ScrolledWindow.__init__(self, hexpand=True, vexpand=False)
        groptions = GrampsOptions("")
        GrampsConfig.__init__(self, grstate, groptions)
        self.obj = obj
        self.obj_type, dummy_var1, dummy_var2 = get_gramps_object_type(obj)

        hbox = Gtk.HBox(hexpand=True, vexpand=False, spacing=3)
        viewport = Gtk.Viewport()
        viewport.add(hbox)
        self.add(viewport)
        self.set_policy(hscrollbar_policy=Gtk.PolicyType.AUTOMATIC, vscrollbar_policy=Gtk.PolicyType.NEVER)

        media_list = self.collect_media()
        if media_list:
#            if self.get_option("sort-by-date"):
#                media_list.sort(
#                    key=lambda x: x[0].get_date_object().get_sort_value()
#                )

            for (media, media_ref) in media_list:
                frame = GrampsImageViewFrame(
                    grstate,
                    media,
                    media_ref
                )
                hbox.pack_start(frame, False, False, 0)
        self.show_all()


    def collect_media(self):
        """
        Helper to collect the media for the current object.
        """
        media_list = []
        self.extract_media(media_list, self.obj)
        return media_list

    def extract_media(self, media_list, obj):
        """
        Helper to extract a set of media references from an object.
        """
        if not hasattr(obj, "media_list"):
            return
        
        obj_type, dummy_var1, dummy_var2 = get_gramps_object_type(obj)
        query_method = self.grstate.dbstate.db.method(
            "get_%s_from_handle", obj_type
        )

        for media_ref in obj.get_media_list():
            media = self.grstate.dbstate.db.get_media_from_handle(
                media_ref.ref
            )
            media_list.append((media, media_ref))
