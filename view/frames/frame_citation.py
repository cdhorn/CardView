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
CitationFrame
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
from ..actions import action_handler
from ..common.common_const import CITATION_TYPES
from ..common.common_utils import (
    get_confidence,
    get_confidence_color_css,
)
from .frame_primary import PrimaryFrame
from ..menus.menu_utils import menu_item

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CitationFrame Class
#
# ------------------------------------------------------------------------
class CitationFrame(PrimaryFrame):
    """
    The CitationFrame exposes some of the basic facts about a Citation.
    """

    def __init__(self, grstate, groptions, citation, reference=None):
        PrimaryFrame.__init__(self, grstate, groptions, citation)
        self.source = self.fetch("Source", citation.source_handle)
        self.__add_citation_title(self.source, citation)
        self.__add_citation_author(self.source)
        self.__add_citation_page(citation)
        self.__add_citation_date(citation)
        self.__add_citation_publisher(self.source)
        self.__add_citation_reference_type(reference)
        self.__add_citation_reference_desc(reference)
        self.__add_citation_confidence(citation)
        self.enable_drag()
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_citation_title(self, source, citation):
        """
        Add title for frame.
        """
        if self.grstate.config.get("general.link-citation-title-to-source"):
            title = self.get_link(
                source.title,
                "Source",
                source.get_handle(),
            )
        else:
            title = self.get_link(
                source.title,
                "Citation",
                citation.get_handle(),
            )
        self.widgets["title"].pack_start(title, True, False, 0)

    def __add_citation_author(self, source):
        """
        Add author of source cited from.
        """
        if source.author:
            self.add_fact(self.get_label(source.author))

    def __add_citation_page(self, citation):
        """
        Add page cited.
        """
        if citation.page:
            self.add_fact(self.get_label(citation.page))

    def __add_citation_date(self, citation):
        """
        Add citation date.
        """
        citation_date = citation.get_date_object()
        if citation_date:
            if self.get_option("show-date"):
                text = glocale.date_displayer.display(citation_date)
                if text:
                    self.add_fact(self.get_label(text))

            if self.groptions.age_base and (
                self.groptions.context in ["timeline"]
                or self.grstate.config.get("group.citation.show-age")
            ):
                self.load_age(self.groptions.age_base, citation_date)

    def __add_citation_publisher(self, source):
        """
        Add publisher of source cited from.
        """
        if self.get_option("show-publisher") and source.pubinfo:
            self.add_fact(self.get_label(source.pubinfo))

    def __add_citation_reference_type(self, reference):
        """
        Add reference type.
        """
        if (
            self.get_option("show-reference-type")
            and reference
            and reference[1]
        ):
            label = self.get_label(CITATION_TYPES[reference[1]], left=False)
            self.widgets["attributes"].add_fact(label)

    def __add_citation_reference_desc(self, reference):
        """
        Add citation reference description.
        """
        if (
            self.get_option("show-reference-description")
            and reference
            and reference[2]
        ):
            label = self.get_label(reference[2], left=False)
            self.widgets["attributes"].add_fact(label)

    def __add_citation_confidence(self, citation):
        """
        Add citation confidence.
        """
        if self.get_option("show-confidence"):
            label = self.get_label(
                get_confidence(citation.confidence), left=False
            )
            self.widgets["attributes"].add_fact(label)

    def _child_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing for a person.
        """
        return self._primary_drop_handler(dnd_type, obj_or_handle, data)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if self.grstate.config.get("display.use-color-scheme"):
            return get_confidence_color_css(
                self.primary.obj.confidence, self.grstate.config
            )
        return ""

    def add_custom_actions(self, context_menu):
        """
        Add action menu items for the citation.
        """
        if self.groptions.backlink:
            (obj_type, obj_handle) = self.groptions.backlink
            obj = self.fetch(obj_type, obj_handle)
            action = action_handler(
                "Citation", self.grstate, self.primary, obj
            )
            context_menu.append(
                menu_item(
                    "list-remove",
                    _("Remove citation"),
                    action.remove_citation,
                )
            )
        if self.source:
            action = action_handler("Source", self.grstate, self.source)
            context_menu.append(
                menu_item(
                    "gtk-edit",
                    _("Edit citation source"),
                    action.edit_object,
                )
            )
