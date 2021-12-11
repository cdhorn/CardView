#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021       Christopher Horn
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
Field formatting utility functions.
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import displayer as place_displayer

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
_ = glocale.translation.sgettext


def format_single_line_normal(
    event, _dummy_get_label, get_link, description, date, place
):
    """
    Return widgets for a formatted single line event description.
    """
    type_label = get_link(
        description,
        "Event",
        event.get_handle(),
        title=False,
    )
    body = date or ""
    if place:
        body = " ".join((body, _("in"), place)).strip()
    body_label = get_link(
        body,
        "Event",
        event.get_handle(),
        title=False,
    )
    return [(type_label, body_label)]


def format_single_line_abbreviated(
    event, get_label, get_link, description, date, place
):
    """
    Return widgets for a formatted abbreviated single line event description.
    """
    body = description
    if date:
        body = " ".join((body, date))
    if place:
        body = " ".join((body, _("in"), place)).strip()
    body_label = get_link(
        body,
        "Event",
        event.get_handle(),
        title=False,
    )
    return [(body_label, get_label(""))]


def format_split_line_normal(
    event, get_label, get_link, description, date, place
):
    """
    Return widgets for a formatted split line event description.
    """
    widgets = []
    type_label = get_link(
        description,
        "Event",
        event.get_handle(),
        title=False,
    )
    if date:
        date_label = get_link(
            date,
            "Event",
            event.get_handle(),
            title=False,
        )
        widgets.append((type_label, date_label))
    if place:
        place_label = get_link(
            place,
            "Place",
            event.get_place_handle(),
            title=False,
        )
        if date:
            widgets.append((get_label(""), place_label))
        else:
            widgets.append((type_label, place_label))
    if not date and not place:
        widgets.append((type_label, get_label("")))
    return widgets


def format_split_line_abbreviated(
    event, get_label, get_link, description, date, place
):
    """
    Return widgets for a formatted split line abbreviated event description.
    """
    widgets = []
    body = description
    if date:
        body = " ".join((body, date))
        date_label = get_link(
            body,
            "Event",
            event.get_handle(),
            title=False,
        )
        widgets.append((date_label, get_label("")))
    if place:
        if not date:
            body = " ".join((body, place))
        else:
            body = place
        place_label = get_link(
            place,
            "Place",
            event.get_place_handle(),
            title=False,
        )
        widgets.append((place_label, get_label("")))
    if not date and not place:
        type_label = get_link(
            body,
            "Event",
            event.get_handle(),
            title=False,
        )
        widgets.append((type_label, get_label("")))
    return widgets


EVENT_FORMATTERS = {
    1: format_single_line_normal,
    2: format_single_line_normal,
    3: format_single_line_abbreviated,
    4: format_single_line_abbreviated,
    5: format_split_line_normal,
    6: format_split_line_abbreviated,
}


def get_event_labels(grstate, event, args):
    """
    Return labels for rendering an event.
    """
    event_format = args.get("event_format")
    get_link = args.get("get_link")
    get_label = args.get("get_label")

    if event_format in [3, 4, 6]:
        description = event.type.get_abbreviation(
            trans_text=glocale.translation.sgettext
        )
    else:
        description = glocale.translation.sgettext(event.type.xml_str())

    date = glocale.date_displayer.display(event.date)
    if event_format in [1, 3, 5, 6]:
        place = place_displayer.display_event(grstate.dbstate.db, event)
    else:
        place = None

    return EVENT_FORMATTERS[event_format](
        event, get_label, get_link, description, date, place
    )
