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
Citation Placard.
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
from frame_base import BaseProfile
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
# CitationPlacard Class
#
# ------------------------------------------------------------------------


class CitationProfileFrame(Gtk.Frame, BaseProfile):
    
    def __init__(self, dbstate, uistate, citation, space, config, router):
        Gtk.Frame.__init__(self, expand=False)
        BaseProfile.__init__(self, dbstate, uistate, space, config, router)
        self.obj = citation
        self.citation = citation
        self.context = "citation"

        self.source = self.dbstate.db.get_source_from_handle(citation.source_handle)
            
        self.grid = Gtk.Grid(margin_right=3, margin_left=3, margin_top=3, margin_bottom=3, row_spacing=2, column_spacing=2)
        title = Gtk.Label(wrap=True, hexpand=True, halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
        title.set_markup("<b>" + self.source.title + "</b>")
        self.grid.attach(title, 0, 0, 1, 1)

        gramps_id = self.get_gramps_id_label()
        self.grid.attach(gramps_id, 1, 0, 1, 1)

        page = Gtk.Label(hexpand=False, halign=Gtk.Align.START, wrap=True)
        page.set_markup(self.markup.format(self.citation.page))
        self.grid.attach(page, 0, 1, 1, 1)

        column2_row = 1
        if self.option("citation", "show-confidence"):
            confidence = Gtk.Label(hexpand=False, halign=Gtk.Align.END, justify=Gtk.Justification.RIGHT, wrap=True)
            confidence.set_markup(self.markup.format(get_confidence(self.citation.confidence)))
            self.grid.attach(confidence, 1, column2_row, 1, 1)
            column2_row = column2_row + 1

        author = Gtk.Label(hexpand=False, halign=Gtk.Align.START, wrap=True)
        author.set_markup(self.markup.format(self.source.author))
        self.grid.attach(author, 0, 2, 1, 1)

        if self.option("citation", "show-publisher"):
            publisher = Gtk.Label(hexpand=False, halign=Gtk.Align.START, wrap=True)
            publisher.set_markup(self.markup.format(self.source.pubinfo))
            self.grid.attach(publisher, 0, 3, 1, 1)

        self.grid.show_all()
        self.event_box = Gtk.EventBox()
        self.event_box.add(self.grid)
        self.event_box.connect('button-press-event', self.build_action_menu)
        self.add(self.event_box)

