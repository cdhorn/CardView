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
from frame_utils import _CONFIDENCE, get_confidence, get_confidence_color_css


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

CITATION_TYPES = {
    0: _("Direct"),
    1: _("Indirect")
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

    def __init__(self, dbstate, uistate, citation, space, config, router, groups=None, references=[], ref_type=0, ref_desc=""):
        GrampsFrame.__init__(
            self, dbstate, uistate, router, space, config, citation, "citation", groups=groups
        )
        self.citation = citation
        self.references = references
        self.ref_type = ref_type
        self.ref_desc = ref_desc
        self.source = self.dbstate.db.get_source_from_handle(citation.source_handle)

        self.enable_drag()

        title = Gtk.Label(
            wrap=True,
            hexpand=False,
            halign=Gtk.Align.START,
            justify=Gtk.Justification.LEFT,
        )
        title.set_markup("<b>{}</b>".format(self.source.title.replace('&', '&amp;')))
        self.title.pack_start(title, True, False, 0)

        if self.source.author:
            author = self.make_label(self.source.author)
            self.add_fact(author)

        if self.citation.page:
            page = self.make_label(self.citation.page)
            self.add_fact(page)

        if self.option("citation", "show-date"):
            if self.citation.get_date_object():
                text = glocale.date_displayer.display(self.citation.get_date_object())
                if text:
                    self.add_fact(self.make_label(text))
        
        if self.option("citation", "show-publisher"):
            if self.source.pubinfo:
                publisher = self.make_label(self.source.pubinfo)
                self.add_fact(publisher)
        
        if self.option("citation", "show-reference-type"):
            ref_type = self.make_label(CITATION_TYPES[self.ref_type], left=False)
            self.metadata.pack_start(ref_type, False, False, 0)

        if self.option("citation", "show-reference-description"):
            if self.ref_desc:
                ref_desc = self.make_label(self.ref_desc, left=False)
                self.metadata.pack_start(ref_desc, False, False, 0)
        
        if self.option("citation", "show-confidence"):
            confidence = self.make_label(
                get_confidence(self.citation.confidence), left=False
            )
            self.metadata.pack_start(confidence, False, False, 0)
        self.set_css_style()

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.config.get("preferences.profile.person.layout.use-color-scheme"):
            return ""

        return get_confidence_color_css(self.obj.confidence, self.config)

