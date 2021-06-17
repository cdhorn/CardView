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
EventGrampsFrame.
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
from gramps.gen.lib import EventType, EventRoleType, Span
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsFrame
from frame_utils import get_confidence, TextLink, get_key_person_events

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# EventGrampsFrame class
#
# ------------------------------------------------------------------------
class EventGrampsFrame(GrampsFrame):
    """
    The EventGrampsFrame exposes some of the basic facts about an Event.
    """

    def __init__(
        self,
        dbstate,
        uistate,
        space,
        config,
        router,
        anchor_person,
        event,
        event_person,
        relation_to_anchor,
        groups=None,
    ):
        GrampsFrame.__init__(self, dbstate, uistate, space, config, event, "timeline")
        self.event = event
        self.router = router
        self.anchor_person = anchor_person
        self.event_person = event_person
        self.relation_to_anchor = relation_to_anchor

        if self.option("timeline", "show-age"):
            vbox = Gtk.VBox(
                hexpand=True,
                margin_right=3,
                margin_left=3,
                margin_top=3,
                margin_bottom=3,
                spacing=2,
            )
            if anchor_person:
                target_person = anchor_person
            else:
                target_person = event_person
            key_events = get_key_person_events(
                self.dbstate.db, target_person, birth_only=True
            )
            birth = key_events["birth"]

            span = Span(birth.date, event.date)
            if span.is_valid():
                precision = global_config.get("preferences.age-display-precision")
                age = str(span.format(precision=precision).strip("()"))
                text = "{}\n{}".format(_("Age"), age.replace(", ", ",\n"))
                label = Gtk.Label(
                    label=self.markup.format(text),
                    use_markup=True,
                    justify=Gtk.Justification.CENTER,
                )
                vbox.add(label)
            if groups and "age" in groups:
                groups["age"].add_widget(vbox)
            self.body.pack_start(vbox, False, False, 0)

        grid = Gtk.Grid(
            margin_right=3,
            margin_left=3,
            margin_top=3,
            margin_bottom=3,
            row_spacing=2,
            column_spacing=2,
        )
        event_type = glocale.translation.sgettext(event.type.xml_str())
        event_person_name = name_displayer.display(event_person)
        if (
            event_person
            and anchor_person.handle != event_person.handle
            and relation_to_anchor not in ["self", "", None]
        ):
            text = "{} {} {}".format(event_type, _("of"), relation_to_anchor.title())
            if self.enable_tooltips:
                tooltip = "{} {} {}".format(
                    _("Click to view"),
                    event_person_name,
                    _("or right click to select edit."),
                )
            else:
                tooltip = None
            name = TextLink(
                text,
                event_person.handle,
                router,
                "link-person",
                tooltip=tooltip,
                hexpand=True,
            )
        else:
            name = Gtk.Label(hexpand=True, halign=Gtk.Align.START, wrap=True)
            name.set_markup("<b>{}</b>".format(event_type))
        grid.attach(name, 0, 0, 1, 1)

        gramps_id = self.get_gramps_id_label()
        grid.attach(gramps_id, 1, 0, 1, 1)

        source_text, citation_text, confidence_text = self.get_quality_labels()
        column2_row = 1

        date = self.make_label(glocale.date_displayer.display(event.date))
        grid.attach(date, 0, 1, 1, 1)

        if self.option("timeline", "show-source-count"):
            sources = self.make_label(source_text, left=False)
            grid.attach(sources, 1, column2_row, 1, 1)
            column2_row = column2_row + 1

        place = self.make_label(place_displayer.display_event(self.dbstate.db, event))
        grid.attach(place, 0, 2, 1, 1)

        if self.option("timeline", "show-citation-count"):
            citations = self.make_label(citation_text, left=False)
            grid.attach(citations, 1, column2_row, 1, 1)
            column2_row = column2_row + 1

        if self.option("timeline", "show-description"):
            text = event.get_description()
            if not text:
                text = "{} {} {}".format(event_type, _("of"), event_person_name)
            description = self.make_label(text)
            grid.attach(description, 0, 3, 1, 1)

        if self.option("timeline", "show-best-confidence"):
            confidence = self.make_label(confidence_text, left=False)
            grid.attach(confidence, 1, column2_row, 1, 1)
            column2_row = column2_row + 1

        if groups and "data" in groups:
            groups["data"].add_widget(grid)
        self.body.pack_start(grid, False, False, 0)
        if self.option("timeline", "show-image"):
            self.load_image()
            if groups and "image" in groups:
                groups["image"].add_widget(self.image)
            self.body.pack_start(self.image, False, False, 0)
        self.set_css_style()

    def get_quality_labels(self):
        """
        Generate textual description for confidence, source and citation counts.
        """
        sources = []
        confidence = 0
        citations = len(self.event.citation_list)
        if self.event.citation_list:
            for handle in self.event.citation_list:
                citation = self.dbstate.db.get_citation_from_handle(handle)
                if citation.source_handle not in sources:
                    sources.append(citation.source_handle)
                if citation.confidence > confidence:
                    confidence = citation.confidence

        if sources:
            if len(sources) == 1:
                source_text = "1 {}".format(_("Source"))
            else:
                source_text = "{} {}".format(len(sources), _("Sources"))
        else:
            source_text = _("No Sources")

        if citations:
            if citations == 1:
                citation_text = "1 {}".format(_("Citation"))
            else:
                citation_text = "{} {}".format(citations, _("Citations"))
        else:
            citation_text = _("No Citations")

        return source_text, citation_text, get_confidence(confidence)
