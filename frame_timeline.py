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
Timeline generator.
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

from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import EventType, Citation, Span
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_css import add_style
from frame_base import BaseProfile
from frame_image import ImageFrame
from timeline import EVENT_CATEGORIES, RELATIVES, Timeline
from frame_utils import get_relation, get_confidence, TextLink, get_key_person_events


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


# ------------------------------------------------------------------------
#
# Routine to generate a timeline grid view
#
# ------------------------------------------------------------------------

def generate_timeline(dbstate, uistate, person, router, config=None, space="preferences.profile.person"):
    person_cache = {}
    markup = "{}"
    if config.get("{}.layout.use-smaller-detail-font".format(space)):
        markup = "<small>{}</small>"

    border = config.get("{}.layout.border-width".format(space))
    if config.get("{}.timeline.show-image".format(space)):
        right = 0
    else:
        right = border
    if config.get("{}.timeline.show-age".format(space)):
        left = 0
    else:
        left = border        
    css_format = '.frame {{ border-top-width: {}px; border-bottom-width: {}px; border-left-width: {}px; border-right-width: {}px; }}'
                
    categories, relations, ancestors, offspring = get_timeline_filters(space, config)
    timeline = Timeline(dbstate.db, events=categories, relatives=relations)
    timeline.add_person(person.handle, anchor=True, ancestors=ancestors, offspring=offspring)

    view = Gtk.Grid(expand=False, margin_right=3, margin_left=3, margin_top=0, margin_bottom=0, row_spacing=3)
    row = 0
    column = 0
    if config.get("{}.timeline.show-age".format(space)):
        column = 1

    for timeline_event in timeline.events():
        if config.get("{}.timeline.show-age".format(space)):
            age_frame, person_cache = build_age_frame(dbstate.db, person, timeline_event[0], timeline_event[1], person_cache, markup)
            age_frame.set_shadow_type(Gtk.ShadowType.NONE)
            view.attach(age_frame, 0, row, 1, 1)
            css = css_format.format(border, border, border, 0)
            add_style(age_frame, css, "frame")

        event_frame = TimelineProfileFrame(dbstate, uistate, space, config, router, person, timeline_event[0], timeline_event[1], timeline_event[2])
        view.attach(event_frame, column, row, 1, 1)
        css = css_format.format(border, border, left, right)
        add_style(event_frame, css, "frame")
        
        if config.get("{}.timeline.show-image".format(space)):
            image_frame = ImageFrame(dbstate.db, uistate, timeline_event[0], size=0)
            image_frame.set_shadow_type(Gtk.ShadowType.NONE)
            view.attach(image_frame, column + 1, row, 1, 1)
            css = css_format.format(border, border, 0, border)
            add_style(image_frame, css, "frame")
        row = row + 1
    view.show_all()
    return view, row


def build_age_frame(db, anchor_person, event, event_person, person_cache, markup):
    frame = Gtk.Frame(expand=False)
    if anchor_person:
        target_person = anchor_person
    else:
        target_person = event_person
    if target_person.handle in person_cache:
        birth = person_cache[target_person.handle]
    else:
        key_events = get_key_person_events(db, target_person, birth_only=True)
        birth = key_events["birth"]
        person_cache.update({target_person.handle: birth})
        
    span = Span(birth.date, event.date)
    if span.is_valid():
        precision=global_config.get("preferences.age-display-precision")
        age = str(span.format(precision=precision).strip("()"))
        vbox = Gtk.VBox(hexpand=False, margin_right=3, margin_left=3, margin_top=3, margin_bottom=3, spacing=2)
        text = "{}\n{}".format(_("Age"), age.replace(", ", ",\n"))
        label = Gtk.Label(label=markup.format(text), use_markup=True, justify=Gtk.Justification.CENTER)
        vbox.add(label)
        frame.add(vbox)
    return frame, person_cache


def get_quality_labels(db, event):
    sources = []
    confidence = 0
    citations = len(event.citation_list)
    if event.citation_list:
        for handle in event.citation_list:
            citation = db.get_citation_from_handle(handle)
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


def get_timeline_filters(space, config):
    categories = []
    relations = []
    ancestors = 1
    offspring = 1

    for category in EVENT_CATEGORIES:
        if config.get('{}.timeline.show-class-{}'.format(space, category)):
            categories.append(category)

    for relation in RELATIVES:
        if config.get('{}.timeline.show-family-{}'.format(space, relation)):
            relations.append(relation)
    ancestors = config.get('{}.timeline.generations-ancestors'.format(space))
    offspring = config.get('{}.timeline.generations-offspring'.format(space))

    return categories, relations, ancestors, offspring


class TimelineProfileFrame(Gtk.Frame, BaseProfile):

    def __init__(self, dbstate, uistate, space, config, router, anchor_person, event, event_person, relation_to_anchor):
        Gtk.Frame.__init__(self, expand=True, shadow_type=Gtk.ShadowType.NONE)
        BaseProfile.__init__(self, dbstate, uistate, space, config, router)
        self.obj = event

        grid = Gtk.Grid(margin_right=3, margin_left=3, margin_top=3, margin_bottom=3, row_spacing=2, column_spacing=2)

        event_type = glocale.translation.sgettext(event.type.xml_str())
        event_person_name = name_displayer.display(event_person)
        if (event_person and anchor_person.handle != event_person.handle and relation_to_anchor not in ["self", "", None]):
            text = "{} {} {}".format(event_type, _("of"), relation_to_anchor.title())
            if self.enable_tooltips:
                tooltip = "{} {} {}".format(_("Click to view"), event_person_name, _("or right click to select edit."))
            else:
                tooltip = None
            name = TextLink(text, event_person.handle, router, "link-person", tooltip=tooltip, hexpand=True)
        else:
            name = Gtk.Label(hexpand=True, halign=Gtk.Align.START, wrap=True)
            name.set_markup("<b>{}</b>".format(event_type))
        grid.attach(name, 0, 0, 1, 1)

        gramps_id = self.get_gramps_id_label()
        grid.attach(gramps_id, 1, 0, 1, 1)

        source_text, citation_text, confidence_text = get_quality_labels(self.dbstate.db, event)
        column2_row = 1

        date = Gtk.Label(hexpand=False, halign=Gtk.Align.START, wrap=True)
        date.set_markup(self.markup.format(glocale.date_displayer.display(event.date)))
        grid.attach(date, 0, 1, 1, 1)

        if self.option("timeline", "show-source-count"):
            sources = Gtk.Label(hexpand=False, halign=Gtk.Align.END, justify=Gtk.Justification.RIGHT, wrap=True)
            sources.set_markup(self.markup.format(source_text))
            grid.attach(sources, 1, column2_row, 1, 1)
            column2_row = column2_row + 1

        place = Gtk.Label(hexpand=False, halign=Gtk.Align.START, justify=Gtk.Justification.LEFT, wrap=True)
        place.set_markup(self.markup.format(place_displayer.display_event(self.dbstate.db, event)))
        grid.attach(place, 0, 2, 1, 1)

        if self.option("timeline", "show-citation-count"):
            citations = Gtk.Label(hexpand=False, halign=Gtk.Align.END, justify=Gtk.Justification.RIGHT, wrap=True)
            citations.set_markup(self.markup.format(citation_text))
            grid.attach(citations, 1, column2_row, 1, 1)
            column2_row = column2_row + 1

        if self.option("timeline", "show-description"):
            description = Gtk.Label(hexpand=False, halign=Gtk.Align.START, justify=Gtk.Justification.LEFT, wrap=True)
            text = event.get_description()
            if not text:
                text = "{} {} {}".format(event_type, _("of"), event_person_name)
            description.set_markup(self.markup.format(text))
            grid.attach(description, 0, 3, 1, 1)

        if self.option("timeline", "show-best-confidence"):
            confidence = Gtk.Label(hexpand=False, halign=Gtk.Align.END, justify=Gtk.Justification.RIGHT, wrap=True)
            confidence.set_markup(self.markup.format(confidence_text))
            grid.attach(confidence, 1, column2_row, 1, 1)
            column2_row = column2_row + 1

        self.event_box = Gtk.EventBox()
        self.event_box.add(grid)
        self.event_box.connect('button-press-event', self.build_action_menu)
        self.add(self.event_box)


