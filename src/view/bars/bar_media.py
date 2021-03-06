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
MediaBarGroup
"""

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib.mediabase import MediaBase
from gramps.gen.utils.file import media_path_full
from gramps.gui.utils import open_file_with_default_application

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsConfig, GrampsObject, GrampsOptions
from ..common.common_const import BUTTON_PRIMARY, BUTTON_SECONDARY
from ..common.common_utils import button_pressed, button_released
from ..services.service_images import images_service
from ..cards import MediaRefCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaBarGroup Class
#
# ------------------------------------------------------------------------
class MediaBarGroup(Gtk.Box, GrampsConfig):
    """
    The MediaBarGroup class provides a container for managing a horizontal
    scrollable list of media items for a given primary Gramps object.
    """

    def __init__(self, grstate, groptions, obj, css=""):
        mode = grstate.config.get("media-bar.position")
        if mode > 0:
            Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
            self.set_hexpand(False)
            self.set_vexpand(True)
            vertical = True
        else:
            Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
            self.set_hexpand(True)
            self.set_vexpand(False)
            vertical = False
        empty_groptions = GrampsOptions("")
        GrampsConfig.__init__(self, grstate, empty_groptions)
        self.base = GrampsObject(obj)
        self.total = 0
        self.box = self.init_layout(css, vertical)

        media_list = self.collect_media()
        if not media_list:
            return

        minimum = self.grstate.config.get("media-bar.minimum-required")
        if len(media_list) < minimum:
            return

        if self.grstate.config.get("media-bar.sort-by-date"):
            media_list.sort(key=lambda x: x[0].get_date_object().sortval)
        media_list = self.group_by_type(media_list)
        media_list = self.filter_non_photos(media_list)

        size = self.grstate.config.get("media-bar.display-mode") in [3, 4]

        crop = self.grstate.config.get("media-bar.display-mode") in [2, 4]

        for (media, media_ref, dummy_media_type) in media_list:
            card = MediaBarItem(
                grstate,
                empty_groptions,
                self.base.obj,
                media,
                media_ref,
                size=size,
                crop=crop,
            )
            self.box.pack_start(card, False, False, 0)
        self.total = len(media_list)
        self.show_all()

    def init_layout(self, css, vertical):
        """
        Initialize layout.
        """
        card = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        if css:
            provider = Gtk.CssProvider()
            provider.load_from_data(css)
            context = card.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            context.add_class("frame")

        if vertical:
            window = Gtk.ScrolledWindow(hexpand=False, vexpand=True)
            window.set_policy(
                hscrollbar_policy=Gtk.PolicyType.NEVER,
                vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            )
            box = Gtk.VBox(hexpand=False, vexpand=True, spacing=3, margin=3)
        else:
            window = Gtk.ScrolledWindow(hexpand=True, vexpand=False)
            window.set_policy(
                hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                vscrollbar_policy=Gtk.PolicyType.NEVER,
            )
            box = Gtk.HBox(hexpand=True, vexpand=False, spacing=3, margin=3)

        viewport = Gtk.Viewport()
        viewport.add(box)
        window.add(viewport)
        card.add(window)
        self.add(card)
        return box

    def collect_media(self):
        """
        Helper to collect the media for the current object.
        """
        media_list = []
        self.extract_media(media_list, self.base.obj, self.base.obj_type)
        return media_list

    def extract_media(self, media_list, obj, _dummy_obj_type):
        """
        Helper to extract a set of media references from an object.
        """
        if isinstance(obj, MediaBase):
            for media_ref in obj.media_list:
                media = self.fetch("Media", media_ref.ref)
                media_type = ""
                for attribute in media.attribute_list:
                    if attribute.get_type().xml_str() == "Media-Type":
                        media_type = attribute.get_value()
                media_list.append((media, media_ref, media_type))
        return media_list

    def group_by_type(self, media_list):
        """
        Group images by type if needed.
        """
        if self.grstate.config.get("media-bar.group-by-type"):
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
        return media_list

    def filter_non_photos(self, media_list):
        """
        Filter out non-photos if needed.
        """
        if self.grstate.config.get("media-bar.filter-non-photos"):
            other_list = []
            for media in media_list:
                if media[2]:
                    if media[2] in [
                        "Photo",
                        "Tombstone",
                        "Headstone",
                    ]:
                        other_list.append(media)
                else:
                    other_list.append(media)
            media_list = other_list
        return media_list


# ------------------------------------------------------------------------
#
# MediaBarItem Class
#
# ------------------------------------------------------------------------
class MediaBarItem(MediaRefCard):
    """
    A simple class for managing display of a media bar image.
    """

    def __init__(
        self, grstate, groptions, obj, media, media_ref, size=0, crop=False
    ):
        groptions.bar_mode = True
        MediaRefCard.__init__(self, grstate, groptions, obj, media_ref)
        self.set_hexpand(False)
        thumbnail = self.get_thumbnail(media, media_ref, size, crop)
        if thumbnail:
            self.frame.add(thumbnail)
            self.eventbox.add(self.frame)
            self.add(self.eventbox)

        self.enable_drop(
            eventbox=self.eventbox,
            dnd_drop_targets=self.dnd_drop_ref_targets,
            drag_data_received=self.ref_drag_data_received,
        )

    def get_thumbnail(self, media, media_ref, size, crop):
        """
        Get the thumbnail image.
        """
        mobj = media
        if not mobj:
            mobj = self.fetch("Media", media_ref.ref)
        if mobj and mobj.mime[0:5] == "image":
            rectangle = None
            if media_ref and crop:
                rectangle = media_ref.get_rectangle()
            path = media_path_full(self.grstate.dbstate.db, mobj.path)
            pixbuf = images_service.get_thumbnail_image(path, rectangle, size)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            return image
        return None

    def view_photo(self):
        """
        Open the image in the default picture viewer.
        """
        photo_path = media_path_full(
            self.grstate.dbstate.db, self.primary.obj.path
        )
        open_file_with_default_application(photo_path, self.grstate.uistate)

    def ref_button_pressed(self, obj, event):
        """
        Route the ref related action if the card was clicked on.
        """
        if button_pressed(event, BUTTON_PRIMARY):
            self.build_ref_action_menu(obj, event)
            return True
        return False

    def ref_button_released(self, _dummy_obj, event):
        """
        Handle button release.
        """
        if button_released(event, BUTTON_SECONDARY):
            if self.grstate.config.get("media-bar.page-link"):
                self.switch_object(None, None, "Media", self.primary.obj)
            else:
                self.view_photo()
            return True
        return False
