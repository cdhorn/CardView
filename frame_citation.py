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
class CitationGrampsFrame(Gtk.Frame, GrampsFrame):
    
    def __init__(self, dbstate, uistate, citation, space, config, router, meta_group=None, image_group=None, data_group=None):
        Gtk.Frame.__init__(self, expand=False, shadow_type=Gtk.ShadowType.NONE)
        GrampsFrame.__init__(self, dbstate, uistate, space, config, router)
        self.obj = citation
        self.citation = citation
        self.context = "citation"

        self.source = self.dbstate.db.get_source_from_handle(citation.source_handle)

        attributes = Gtk.VBox(vexpand=False)
        if data_group:
            data_group.add_widget(attributes)
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
        if meta_group:
            meta_group.add_widget(metadata)

        gramps_id = self.get_gramps_id_label()
        metadata.pack_start(gramps_id, False, False, 0)

        if self.option("citation", "show-confidence"):
            confidence = self.make_label(get_confidence(self.citation.confidence), left=False)
            metadata.pack_start(confidence, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata.pack_start(flowbox, False, False, 0)

        body = Gtk.HBox()
        body.pack_start(attributes, False, False, 0)
        body.pack_start(metadata, False, False, 0)
        if self.option("citation", "show-image"):
            self.load_image()
            if image_group:
                image_group.add_widget(self.image)
            body.pack_start(self.image, False, False, 0)

        self.event_box = Gtk.EventBox()
        self.event_box.add(body)
        self.event_box.connect('button-press-event', self.build_action_menu)
        self.add(self.event_box)

        self.set_css_style()
