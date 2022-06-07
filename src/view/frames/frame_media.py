#
# Gramps - a GTK+/GNOME based genealogy program
#
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
MediaFrame
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

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..menus.menu_utils import menu_item
from .frame_reference import ReferenceFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaFrame Class
#
# ------------------------------------------------------------------------
class MediaFrame(ReferenceFrame):
    """
    The MediaFrame exposes the image and some facts about Media.
    """

    def __init__(self, grstate, groptions, media, reference_tuple=None):
        ReferenceFrame.__init__(
            self, grstate, groptions, media, reference_tuple=reference_tuple
        )
        if not groptions.bar_mode:
            self.__add_media_title(media)
            self.__add_media_date(media)
            self.__add_media_path(media)
            self.__add_media_mime_type(media)
            self.enable_drag()
            self.enable_drop(
                self.eventbox, self.dnd_drop_targets, self.drag_data_received
            )
            self.set_css_style()

    def __add_media_title(self, media):
        """
        Add media title.
        """
        title = self.get_link(
            media.get_description(),
            "Media",
            media.handle,
        )
        self.widgets["title"].pack_start(title, True, False, 0)

    def __add_media_date(self, media):
        media_date = media.get_date_object()
        if media_date:
            if self.get_option("show-date"):
                text = glocale.date_displayer.display(media_date)
                if text:
                    self.add_fact(self.get_label(text))

            age_base = self.groptions.age_base
            if age_base and (
                self.groptions.context in ["timeline"]
                or self.grstate.config.get("group.media.show-age")
            ):
                self.load_age(age_base, media_date)

    def __add_media_path(self, media):
        """
        Add media path.
        """
        if self.get_option("show-path") and media.path:
            self.add_fact(self.get_label(media.path))

    def __add_media_mime_type(self, media):
        """
        Add media mime type.
        """
        if self.get_option("show-mime-type") and media.mime:
            self.add_fact(self.get_label(media.mime))

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing.
        """
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def build_layout(self):
        """
        Construct framework for media layout, overrides base class.
        """
        if self.groptions.bar_mode:
            return

        active = "active" in self.groptions.option_space
        crop = self.get_option("image-mode") in [2, 4]
        size = 0
        if self.get_option("image-mode") in [3, 4]:
            size = 2

        if self.reference:
            self.load_image(size, media_ref=self.reference.obj, crop=crop)
        else:
            self.load_image(size, crop=crop)

        if not active and "age" in self.widgets and self.groptions.age_base:
            self.widgets["body"].pack_start(
                self.widgets["age"], expand=False, fill=False, padding=0
            )
            if "age" in self.groptions.size_groups:
                self.groptions.size_groups["age"].add_widget(
                    self.widgets["age"]
                )
        hcontent = Gtk.HBox(hexpand=False)
        self.widgets["body"].pack_start(
            hcontent, expand=True, fill=True, padding=0
        )

        if active:
            hcontent.pack_start(
                self.widgets["image"], expand=False, fill=False, padding=3
            )

        fact_block = Gtk.VBox(halign=Gtk.Align.START, hexpand=True)
        if "data" in self.groptions.size_groups:
            self.groptions.size_groups["data"].add_widget(fact_block)
        fact_block.pack_start(
            self.widgets["title"], expand=True, fill=True, padding=0
        )
        if active:
            fact_block.pack_start(
                self.widgets["facts"], expand=True, fill=True, padding=0
            )
        else:
            ncontent = Gtk.HBox(hexpand=True)
            ncontent.pack_start(
                self.widgets["image"], expand=False, fill=False, padding=3
            )
            ncontent.pack_start(
                self.widgets["facts"], expand=True, fill=True, padding=0
            )
            fact_block.pack_start(ncontent, expand=True, fill=True, padding=0)

        fact_block.pack_start(
            self.widgets["icons"], expand=True, fill=True, padding=0
        )
        hcontent.pack_start(fact_block, expand=True, fill=True, padding=0)

        attribute_block = Gtk.VBox(halign=Gtk.Align.END, hexpand=False)
        if "attributes" in self.groptions.size_groups:
            self.groptions.size_groups["attributes"].add_widget(
                attribute_block
            )
        attribute_block.pack_start(
            self.widgets["id"], expand=False, fill=False, padding=0
        )
        attribute_block.pack_start(
            self.widgets["attributes"], expand=False, fill=False, padding=0
        )
        hcontent.pack_start(
            attribute_block, expand=False, fill=False, padding=0
        )

    def add_custom_actions(self, context_menu):
        """
        Add action menu items specific for the image.
        """
        if self.groptions.backlink:
            (obj_type, obj_handle) = self.groptions.backlink
            target_object = self.fetch(obj_type, obj_handle)
            action = action_handler(
                "Media", self.grstate, self.primary, target_object
            )
            context_menu.append(
                menu_item(
                    "gramps-media",
                    _("Make active media"),
                    action.set_active_media,
                )
            )
