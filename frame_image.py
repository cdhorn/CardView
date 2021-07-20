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
from gramps.gen.display.place import PlaceDisplay


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_class import GrampsFrame
from frame_utils import TextLink


# ------------------------------------------------------------------------
#
# Internationalisation
#
# ------------------------------------------------------------------------

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

pd = PlaceDisplay()


# ------------------------------------------------------------------------
#
# ImageGrampsFrame Class
#
# ------------------------------------------------------------------------
class ImageGrampsFrame(GrampsFrame):
    """
    The ImageGrampsFrame exposes the image and some facts about Media.
    """

    def __init__(self, grstate, context, media, groups=None):
        GrampsFrame.__init__(self, grstate, context, media, groups=groups)

        title = TextLink(
            media.get_description(),
            "Media",
            media.get_handle(),
            self.switch_object,
            bold=True
        )
        self.title.pack_start(title, True, False, 0)

        if self.option("media", "show-date"):
            if media.get_date_object():
                text = glocale.date_displayer.display(media.get_date_object())
                if text:
                    self.add_fact(self.make_label(text))

        self.enable_drag()
        self.set_css_style()

    def build_layout(self):
        """
        Construct framework for media layout, overrides base class.
        """
        self.load_image(2)
        vcontent = Gtk.VBox()
        self.body.pack_start(vcontent, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.image, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.title, expand=True, fill=True, padding=0)
        vcontent.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        hcontent = Gtk.HBox(hexpand=True)
        hcontent.pack_start(self.tags, expand=True, fill=True, padding=0)
        hcontent.pack_start(self.metadata, expand=True, fill=True, padding=0)
        vcontent.pack_start(hcontent, expand=True, fill=True, padding=0)
