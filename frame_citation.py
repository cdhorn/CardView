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
from gi.repository import Gtk, GdkPixbuf


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventType, Citation, Span
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.display.place import PlaceDisplay


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsFrame
from frame_utils import get_relation, get_confidence, TextLink


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
# CitationGrampsFrame Class
#
# ------------------------------------------------------------------------
class CitationGrampsFrame(GrampsFrame):
    
    def __init__(self, dbstate, uistate, citation, space, config, router, groups=None):
        GrampsFrame.__init__(self, dbstate, uistate, space, config, router)
        self.set_object(citation, "citation")
        self.citation = citation

        self.source = self.dbstate.db.get_source_from_handle(citation.source_handle)

        attributes = Gtk.VBox(vexpand=False)
        if groups and "data" in groups:
            groups["data"].add_widget(attributes)
        title = Gtk.Label(wrap=True, hexpand=False, halign=Gtk.Align.START, justify=Gtk.Justification.LEFT)
        title.set_markup("<b>" + self.source.title + "</b>")
        attributes.pack_start(title, True, False, 0)

        if self.source.author:
            author = self.make_label(self.source.author)
            attributes.pack_start(author, False, False, 0)

        if self.source.pubinfo:
            publisher = self.make_label(self.source.pubinfo)
            attributes.pack_start(publisher, False, False, 0)

        if self.citation.page:
            page = self.make_label(self.citation.page)
            attributes.pack_start(page, False, False, 0)

        metadata = Gtk.VBox()
        if groups and "metadata" in groups:
            groups["metadata"].add_widget(metadata)

        gramps_id = self.get_gramps_id_label()
        metadata.pack_start(gramps_id, False, False, 0)

        if self.option("citation", "show-confidence"):
            confidence = self.make_label(get_confidence(self.citation.confidence), left=False)
            metadata.pack_start(confidence, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata.pack_start(flowbox, False, False, 0)

        if groups:
            if "data" in groups:
                groups["data"].add_widget(attributes)
            if "metadata" in groups:
                groups["metadata"].add_widget(metadata)
        self.body.pack_start(attributes, False, False, 0)
        self.body.pack_start(metadata, False, False, 0)
        if self.option("citation", "show-image"):
            self.load_image()
            if groups and "image" in groups:
                groups["image"].add_widget(self.image)
            self.body.pack_start(self.image, False, False, 0)
        self.set_css_style()
