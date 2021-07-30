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
CitationGrampsFrame
"""

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
from frame_primary import PrimaryGrampsFrame
from frame_utils import get_confidence, get_confidence_color_css, TextLink


try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

CITATION_TYPES = {
    0: _("Direct"),
    1: _("Indirect")
}


# ------------------------------------------------------------------------
#
# CitationGrampsFrame Class
#
# ------------------------------------------------------------------------
class CitationGrampsFrame(PrimaryGrampsFrame):
    """
    The CitationGrampsFrame exposes some of the basic facts about a Citation.
    """

    def __init__(self, grstate, context, citation, groups=None, reference=None):
        PrimaryGrampsFrame.__init__(self, grstate, "citation", citation, groups=groups)
        source = grstate.dbstate.db.get_source_from_handle(citation.source_handle)

        if grstate.config.get("options.global.link-citation-title-to-source"):
            title = TextLink(source.title, "Source", source.get_handle(), self.switch_object, bold=True)
        else:
            title = TextLink(source.title, "Citation", citation.get_handle(), self.switch_object, bold=True)
        self.title.pack_start(title, True, False, 0)

        if source.author:
            self.add_fact(self.make_label(source.author))

        if citation.page:
            self.add_fact(self.make_label(citation.page))

        if self.option("citation", "show-date"):
            if citation.get_date_object():
                text = glocale.date_displayer.display(citation.get_date_object())
                if text:
                    self.add_fact(self.make_label(text))

        if self.option("citation", "show-publisher"):
            if source.pubinfo:
                self.add_fact(self.make_label(source.pubinfo))

        if self.option("citation", "show-reference-type"):
            if reference and reference[1]:
                label = self.make_label(CITATION_TYPES[reference[1]], left=False)
                self.metadata.pack_start(label, False, False, 0)

        if self.option("citation", "show-reference-description"):
            if reference and reference[2]:
                label = self.make_label(reference[2], left=False)
                self.metadata.pack_start(label, False, False, 0)

        if self.option("citation", "show-confidence"):
            label = self.make_label(get_confidence(citation.confidence), left=False)
            self.metadata.pack_start(label, False, False, 0)

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.option("page", "use-color-scheme"):
            return ""

        return get_confidence_color_css(self.obj.confidence, self.grstate.config)
