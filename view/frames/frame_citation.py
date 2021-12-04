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
from ..common.common_const import CITATION_TYPES
from ..common.common_utils import (
    TextLink,
    get_confidence,
    get_confidence_color_css,
    menu_item,
)
from .frame_primary import PrimaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CitationGrampsFrame Class
#
# ------------------------------------------------------------------------
class CitationGrampsFrame(PrimaryGrampsFrame):
    """
    The CitationGrampsFrame exposes some of the basic facts about a Citation.
    """

    def __init__(self, grstate, groptions, citation, reference=None):
        PrimaryGrampsFrame.__init__(self, grstate, groptions, citation)
        self.source = self.fetch("Source", citation.source_handle)
        self.populate_layout(self.source, citation, reference)
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def populate_layout(self, source, citation, reference=None):
        """
        Populate information.
        """
        if self.grstate.config.get(
            "options.global.link-citation-title-to-source"
        ):
            title = TextLink(
                source.title,
                "Source",
                source.get_handle(),
                self.switch_object,
                bold=True,
            )
        else:
            title = TextLink(
                source.title,
                "Citation",
                citation.get_handle(),
                self.switch_object,
                bold=True,
            )
        self.widgets["title"].pack_start(title, True, False, 0)

        if source.author:
            self.add_fact(self.make_label(source.author))

        if citation.page:
            self.add_fact(self.make_label(citation.page))

        if citation.get_date_object():
            if self.get_option("show-date"):
                text = glocale.date_displayer.display(
                    citation.get_date_object()
                )
                if text:
                    self.add_fact(self.make_label(text))

            if self.groptions.age_base:
                if self.groptions.context in ["timeline"]:
                    self.load_age(
                        self.groptions.age_base, citation.get_date_object()
                    )
                elif self.grstate.config.get(
                    "options.group.citation.show-age"
                ):
                    self.load_age(
                        self.groptions.age_base, citation.get_date_object()
                    )

        if self.get_option("show-publisher"):
            if source.pubinfo:
                self.add_fact(self.make_label(source.pubinfo))

        if self.get_option("show-reference-type"):
            if reference and reference[1]:
                label = self.make_label(
                    CITATION_TYPES[reference[1]], left=False
                )
                self.widgets["attributes"].add_fact(label)

        if self.get_option("show-reference-description"):
            if reference and reference[2]:
                label = self.make_label(reference[2], left=False)
                self.widgets["attributes"].add_fact(label)

        if self.get_option("show-confidence"):
            label = self.make_label(
                get_confidence(citation.confidence), left=False
            )
            self.widgets["attributes"].add_fact(label)
        self.show_all()

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("options.global.use-color-scheme"):
            return ""

        return get_confidence_color_css(
            self.primary.obj.confidence, self.grstate.config
        )

    def add_custom_actions(self, action_menu):
        """
        Add action menu items for the citation.
        """
        action_menu.append(
            menu_item(
                "gtk-edit",
                _("Edit citation source"),
                self.edit_citation_source,
            )
        )

    def edit_citation_source(self, *_dummy_args):
        """
        Edit citation source.
        """
        self.edit_primary_object(obj=self.source, obj_type="Source")
