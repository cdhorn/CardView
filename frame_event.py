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
from timeline import RELATIVES

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
        event_person,
        relation_to_reference,
        groups=None,
    ):
        GrampsFrame.__init__(self, dbstate, uistate, router, space, config, event, "timeline")
        self.event = event
        self.reference_person = reference_person
        self.event_person = event_person
        self.relation_to_reference = relation_to_reference

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

        event_type = glocale.translation.sgettext(event.type.xml_str())
        event_person_name = name_displayer.display(event_person)
        if (
            event_person
            and reference_person.handle != event_person.handle
            and relation_to_reference not in ["self", "", None]
        ):
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
            name.set_markup("<b>{}</b>".format(event_type))
        data.pack_start(name, True, True, 0)

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

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.config.get(
                "preferences.profile.person.layout.use-color-scheme"
        ):
            return ""

        key = None
        if self.relation_to_reference == "self":
            key = "active"
        else:
            for relative in RELATIVES:
                if relative in ["wife", "husband"]:
                    if "spouse" in self.relation_to_reference:
                        key = "spouse"
                elif relative in self.relation_to_reference:
                    key = relative
                    break
        if not key:
            return ""
        
        background_color = self.config.get("preferences.profile.colors.relations.{}".format(key))
        border_color = self.config.get("preferences.profile.colors.relations.border-{}".format(key))
        
        scheme = global_config.get("colors.scheme")
        css = ""
        if background_color:
            css = "background-color: {};".format(background_color[scheme])
        if border_color:
            css = "{} border-color: {};".format(css, border_color[scheme])
        return css        
