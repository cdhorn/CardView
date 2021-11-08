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
ImageGrampsFrame
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

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsObject
from ..common.common_utils import TextLink
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# ImageGrampsFrame Class
#
# ------------------------------------------------------------------------
class ImageGrampsFrame(PrimaryGrampsFrame):
    """
    The ImageGrampsFrame exposes the image and some facts about Media.
    """

    def __init__(self, grstate, groptions, media, media_ref=None):
        PrimaryGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            media,
        )
        self.reference = GrampsObject(media_ref)

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

        if media.get_path():
            self.add_fact(self.make_label(media.get_path()))

        if media.get_mime_type():
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

        tbox = Gtk.HBox(hexpand=False, vexpand=False)
        tbox.pack_start(self.widgets["tags"], False, False, 0)
        if active:
            hcontent = Gtk.HBox(hexpand=True)
            hcontent.pack_start(
                self.widgets["image"], expand=False, fill=False, padding=0
            )
            fact_block = Gtk.VBox()
            fact_block.pack_start(
                self.widgets["title"], expand=True, fill=True, padding=0
            )
            fact_block.pack_start(
                self.widgets["facts"], expand=True, fill=True, padding=0
            )
            fact_block.pack_start(tbox, expand=True, fill=False, padding=0)
            hcontent.pack_start(fact_block, expand=True, fill=True, padding=0)
            attribute_block = Gtk.VBox()
            attribute_block.pack_start(
                self.widgets["id"], expand=False, fill=True, padding=0
            )
            attribute_block.pack_start(
                self.widgets["attributes"], expand=False, fill=True, padding=0
            )
            hcontent.pack_start(
                attribute_block, expand=True, fill=True, padding=0
            )
            self.widgets["body"].pack_start(
                hcontent, expand=True, fill=True, padding=0
            )
        else:
            if "age" in self.widgets and self.groptions.age_base:
                self.widgets["body"].pack_start(
                    self.widgets["age"], expand=False, fill=False, padding=0
                )
            vcontent = Gtk.VBox(hexpand=False)
            self.widgets["body"].pack_start(
                vcontent, expand=True, fill=True, padding=0
            )

            image_block = Gtk.HBox(hexpand=False)
            image_block.pack_start(
                self.widgets["image"], expand=True, fill=True, padding=0
            )
            image_block.pack_end(
                self.widgets["attributes"], expand=False, fill=True, padding=0
            )

            header_block = Gtk.HBox(hexpand=False)
            title_block = Gtk.VBox(hexpand=False)
            title_block.pack_start(
                self.widgets["title"], expand=True, fill=True, padding=0
            )
            title_block.pack_start(tbox, expand=True, fill=False, padding=0)
            header_block.pack_start(title_block, True, True, 0)

            meta_block = Gtk.VBox(hexpand=False)
            meta_block.pack_start(
                self.widgets["id"], expand=True, fill=True, padding=0
            )
            header_block.pack_start(meta_block, True, True, 0)

            if self.get_option("image-on-top"):
                vcontent.pack_start(image_block, True, True, 0)
                vcontent.pack_start(header_block, True, True, 0)
            else:
                vcontent.pack_start(header_block, True, True, 0)
                vcontent.pack_start(image_block, True, True, 0)
