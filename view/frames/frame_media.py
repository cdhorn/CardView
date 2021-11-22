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
MediaGrampsFrame
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
from ..common.common_utils import TextLink, menu_item
from .frame_reference import ReferenceGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# MediaGrampsFrame Class
#
# ------------------------------------------------------------------------
class MediaGrampsFrame(ReferenceGrampsFrame):
    """
    The MediaGrampsFrame exposes the image and some facts about Media.
    """

    def __init__(self, grstate, groptions, media, reference_tuple=None):
        ReferenceGrampsFrame.__init__(
            self, grstate, groptions, media, reference_tuple=reference_tuple
        )

        title = TextLink(
            media.get_description(),
            "Media",
            media.get_handle(),
            self.switch_object,
            bold=True,
        )
        self.widgets["title"].pack_start(title, True, False, 0)

        if media.get_date_object():
            if self.get_option("show-date"):
                text = glocale.date_displayer.display(media.get_date_object())
                if text:
                    self.add_fact(self.make_label(text))

            if "age" in self.widgets and groptions.age_base:
                self.load_age(groptions.age_base, media.get_date_object())

        if self.get_option("show-path") and media.get_path():
            self.add_fact(self.make_label(media.get_path()))

        if self.get_option("show-mime-type") and media.get_mime_type():
            self.add_fact(self.make_label(media.get_mime_type()))

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def build_layout(self):
        """
        Construct framework for media layout, overrides base class.
        """
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

    def add_custom_actions(self, action_menu):
        """
        Add action menu items specific for the image.
        """
        if self.groptions.backlink:
            action_menu.append(
                menu_item(
                    "gramps-media",
                    _("Make active media"),
                    self._make_active_media,
                )
            )

    def _make_active_media(self, _dummy_var1):
        """
        Make the image the active media item.
        """
        (obj_type, obj_handle) = self.groptions.backlink
        obj = self.grstate.fetch(obj_type, obj_handle)

        new_list = []
        image_ref = None
        image_handle = self.primary.obj.get_handle()
        for media_ref in obj.get_media_list():
            if media_ref.ref == image_handle:
                image_ref = media_ref
            else:
                new_list.append(media_ref)
        if image_ref:
            new_list.insert(0, image_ref)

        message = " ".join(
            (
                _("Set"),
                _("Image"),
                self.primary.obj.get_gramps_id(),
                _("Active"),
                _("for"),
                obj_type,
                obj.get_gramps_id(),
            )
        )
        commit_method = self.grstate.dbstate.db.method("commit_%s", obj_type)
        with DbTxn(message, self.grstate.dbstate.db) as trans:
            obj.set_media_list(new_list)
            commit_method(obj, trans)
