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
CitationGrampsFrame.
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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import PlaceDisplay
from gramps.gen.lib import Citation


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsFrame
from frame_utils import get_confidence, _CONFIDENCE


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

CONFIDENCE_COLOR_SCHEME = {
    Citation.CONF_VERY_LOW: "very-low",
    Citation.CONF_LOW: "low",
    Citation.CONF_NORMAL: "normal",
    Citation.CONF_HIGH: "high",
    Citation.CONF_VERY_HIGH: "very-high",
}    


# ------------------------------------------------------------------------
#
# CitationGrampsFrame Class
#
# ------------------------------------------------------------------------
class CitationGrampsFrame(GrampsFrame):
    """
    The CitationGrampsFrame exposes some of the basic facts about a Citation.
    """

    def __init__(self, dbstate, uistate, citation, space, config, router, groups=None):
        GrampsFrame.__init__(
            self, dbstate, uistate, router, space, config, citation, "citation"
        )
        self.citation = citation
        self.source = self.dbstate.db.get_source_from_handle(citation.source_handle)

        if self.option(self.context, "show-image"):
            self.load_image(groups)
            if self.option(self.context, "show-image-first"):
                self.body.pack_start(self.image, expand=False, fill=False, padding=0)

        data = Gtk.VBox(vexpand=False)
        if groups and "data" in groups:
            groups["data"].add_widget(data)
        self.body.pack_start(data, False, False, 0)

        title = Gtk.Label(
            wrap=True,
            hexpand=False,
            halign=Gtk.Align.START,
            justify=Gtk.Justification.LEFT,
        )
        title.set_markup("<b>{}</b>".format(self.source.title.replace('&', '&amp;')))
        data.pack_start(title, True, False, 0)

        if self.source.author:
            author = self.make_label(self.source.author)
            data.pack_start(author, False, False, 0)

        if self.citation.page:
            page = self.make_label(self.citation.page)
            data.pack_start(page, False, False, 0)

        if self.option("citation", "show-date"):
            if self.citation.get_date_object():
                text = glocale.date_displayer.display(self.citation.get_date_object())
                if text:
                    data.pack_start(self.make_label(text), False, False, 0)
        
        if self.option("citation", "show-publisher"):
            if self.source.pubinfo:
                publisher = self.make_label(self.source.pubinfo)
                data.pack_start(publisher, False, False, 0)
        
        metadata = Gtk.VBox()
        if groups and "metadata" in groups:
            groups["metadata"].add_widget(metadata)
        self.body.pack_start(metadata, False, False, 0)

        gramps_id = self.get_gramps_id_label()
        metadata.pack_start(gramps_id, False, False, 0)

        if self.option("citation", "show-confidence"):
            confidence = self.make_label(
                get_confidence(self.citation.confidence), left=False
            )
            metadata.pack_start(confidence, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata.pack_start(flowbox, False, False, 0)

        if self.option(self.context, "show-image"):
            if not self.option(self.context, "show-image-first"):
                self.body.pack_start(self.image, False, False, 0)
        self.set_css_style()

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.config.get(
                "preferences.profile.person.layout.use-color-scheme"
        ):
            return ""
        
        key = CONFIDENCE_COLOR_SCHEME[self.obj.confidence]
        background_color = self.config.get("preferences.profile.colors.confidence.{}".format(key))
        border_color = self.config.get("preferences.profile.colors.confidence.border-{}".format(key))
        
        scheme = global_config.get("colors.scheme")
        css = ""
        if background_color:
            css = "background-color: {};".format(background_color[scheme])
        if border_color:
            css = "{} border-color: {};".format(css, border_color[scheme])
        return css        
