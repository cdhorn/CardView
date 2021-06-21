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
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import get_participant_from_event


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsFrame
from frame_utils import (
    get_confidence,
    get_confidence_color_css,
    get_event_category_color_css,
    get_key_person_events,
    get_participants,
    get_person_color_css,
    get_relationship_color_css,
    TextLink,
)

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
        reference_person,
        event,
        event_ref,
        event_person,
        relation_to_reference,
        category=None,
        groups=None,
    ):
        GrampsFrame.__init__(self, dbstate, uistate, router, space, config, event, "timeline")
        self.event = event
        self.event_ref = event_ref
        self.event_category = category
        self.reference_person = reference_person
        self.event_person = event_person
        self.relation_to_reference = relation_to_reference
        self.confidence = 0

        if self.option(self.context, "show-image"):
            self.load_image(groups)
            if self.option(self.context, "show-image-first"):
                self.body.pack_start(self.image, expand=False, fill=False, padding=0)
        
        if self.option(self.context, "show-age"):
            age_vbox = Gtk.VBox(
                hexpand=True,
                margin_right=3,
                margin_left=3,
                margin_top=3,
                margin_bottom=3,
                spacing=2,
            )
            if reference_person:
                target_person = reference_person
            else:
                target_person = event_person
            key_events = get_key_person_events(
                self.dbstate.db, target_person, birth_only=True
            )
            birth = key_events["birth"]

            if birth and birth.date and event.date:
                span = Span(birth.date, event.date)
                if span.is_valid():
                    year = event.date.get_year()
                    if birth.handle == event.handle:
                        text = "<b>{}</b>".format(year)
                    else:
                        precision = global_config.get("preferences.age-display-precision")
                        age = str(span.format(precision=precision).strip("()"))
                        text = "<b>{}</b>\n{}".format(year, age.replace(", ", ",\n"))
                    label = Gtk.Label(
                        label=self.markup.format(text),
                        use_markup=True,
                        justify=Gtk.Justification.CENTER,
                    )
                    age_vbox.add(label)
            if groups and "age" in groups:
                groups["age"].add_widget(age_vbox)
            if not self.option(self.context, "show-image-first"):
                self.body.pack_start(age_vbox, False, False, 0)

        data = Gtk.VBox()
        if groups and "data" in groups:
            groups["data"].add_widget(data)
        self.body.pack_start(data, True, True, 0)

        role = None
        if self.reference_person and self.reference_person.handle == self.event_person.handle:
            role = self.event_ref.get_role()

        event_type = glocale.translation.sgettext(event.type.xml_str())
        event_person_name = name_displayer.display(event_person)
        if (event_person and not role and relation_to_reference not in ["self", "", None]):
            text = "{} {} {}".format(event_type, _("of"), relation_to_reference.title())
            if self.enable_tooltips:
                tooltip = "{} {}".format(
                    _("Click to view"),
                    event_person_name,
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
            label = event_type
            if not role.is_primary() and not role.is_family():
                text = event.get_description()                
                if text:
                    label = text
            name.set_markup("<b>{}</b>".format(label))
        data.pack_start(name, True, True, 0)

        if (
                (role and not role.is_primary() and not role.is_family()) or
                self.option(self.context, "show-role-always")
        ):
            data.pack_start(self.make_label(str(role)), True, True, 0)

        date = glocale.date_displayer.display(event.date)
        if date:
            data.pack_start(self.make_label(date), True, True, 0)

        place = place_displayer.display_event(self.dbstate.db, event)
        if place:
            data.pack_start(self.make_label(place), True, True, 0)

        if self.option(self.context, "show-description"):
            text = event.get_description()
            if not text:
                text = "{} {} {}".format(event_type, _("of"), event_person_name)
            data.pack_start(self.make_label(text), True, True, 0)

        if self.option(self.context, "show-participants"):
            participants, text = get_participants(self.dbstate.db, event)
            if text and len(participants) > 1:
                data.pack_start(self.make_label("Participants {}".format(text)), True, True, 0)

        source_text, citation_text, confidence_text = self.get_quality_labels()
        text = ""
        comma = ""
        if self.option(self.context, "show-source-count") and source_text:
            text = source_text
            comma = ", "
        if self.option(self.context, "show-citation-count") and citation_text:
            text = "{}{}{}".format(text, comma, citation_text)
            comma = ", "
        if self.option(self.context, "show-best-confidence") and confidence_text:
            text = "{}{}{}".format(text, comma, confidence_text)
        if text:
            data.pack_start(self.make_label(text.lower().capitalize()), True, True, 0)

        metadata = Gtk.VBox()
        if groups and "metadata" in groups:
            groups["metadata"].add_widget(metadata)
        self.body.pack_start(metadata, False, False, 0)

        gramps_id = self.get_gramps_id_label()
        metadata.pack_start(gramps_id, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            metadata.pack_start(flowbox, False, False, 0)

        if self.option(self.context, "show-image"):
             if not self.option(self.context, "show-image-first"):
                 self.body.pack_start(self.image, False, False, 0)
             else:
                 if self.option(self.context, "show-age"):
                     self.body.pack_start(age_vbox, False, False, 0)                     
        self.set_css_style()
            
    def get_quality_labels(self):
        """
        Generate textual description for confidence, source and citation counts.
        """
        sources = []
        citations = len(self.event.citation_list)
        if self.event.citation_list:
            for handle in self.event.citation_list:
                citation = self.dbstate.db.get_citation_from_handle(handle)
                if citation.source_handle not in sources:
                    sources.append(citation.source_handle)
                if citation.confidence > self.confidence:
                    self.confidence = citation.confidence

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

        return source_text, citation_text, get_confidence(self.confidence)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.config.get(
                "preferences.profile.person.layout.use-color-scheme"
        ):
            return ""

        scheme = self.option("timeline", "color-scheme")
        if scheme == 1:
            return get_relationship_color_css(self.relation_to_reference, self.config)
        if scheme == 2:
            return get_event_category_color_css(self.event_category, self.config)
        if scheme == 3:
            return get_confidence_color_css(self.confidence, self.config)

        living = probably_alive(self.event_person, self.dbstate.db)
        return get_person_color_css(self.event_person, self.config, living=living)
