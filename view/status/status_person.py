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
Person status indicators.
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
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.editors import EditEvent

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsBaseIcon
from ..common.common_utils import menu_item, prepare_icon
from ..config.config_utils import get_event_fields
from .status_utils import get_status_ranking

_ = glocale.translation.sgettext

RANK_ICONS = {
    1: "non-starred",
    2: "semi-starred",
    3: "semi-starred-rtl",
    4: "starred",
}

RANK_OPTIONS = {
    "options.global.status.rank-object": "object",
    "options.global.status.rank-names": "names",
    "options.global.status.rank-events": "events",
    "options.global.status.rank-ordinances": "ordinances",
    "options.global.status.rank-attributes": "attributes",
    "options.global.status.rank-associations": "associations",
    "options.global.status.rank-addresses": "addresses",
    "options.global.status.rank-spouses": "spouses",
    "options.global.status.rank-children": "children",
}


# ------------------------------------------------------------------------
#
# GrampsCitationAlertIcon class
#
# ------------------------------------------------------------------------
class GrampsCitationAlertIcon(GrampsBaseIcon):
    """
    A class to manage the icon and access to the citation alert items.
    """

    def __init__(self, grstate, alert_list):
        if len(alert_list) > 1:
            tooltip = " ".join((str(len(alert_list)), _("Citation Alerts")))
        else:
            tooltip = " ".join(("1", _("Citation Alert")))
        GrampsBaseIcon.__init__(
            self, grstate, "software-update-urgent", tooltip=tooltip
        )
        self.alert_list = alert_list

    def icon_clicked(self, event):
        """
        Build alert context menu.
        """
        menu = Gtk.Menu()
        if self.grstate.config.get(
            "options.global.status.citation-alert-edit"
        ):
            callback = self.edit_event
        else:
            callback = self.goto_event
        for (alert_event, alert_text) in self.alert_list:
            menu.append(
                menu_item("gramps-event", alert_text, callback, alert_event)
            )
        menu.attach_to_widget(self, None)
        menu.show_all()
        if Gtk.get_minor_version() >= 22:
            menu.popup_at_pointer(event)
        else:
            menu.popup(None, None, None, None, event.button, event.time)
        return True

    def goto_event(self, _dummy_event, event):
        """
        Go to the event page.
        """
        self.grstate.load_primary_page("Event", event)

    def edit_event(self, _dummy_event, event):
        """
        Open event in editor.
        """
        try:
            EditEvent(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                event,
            )
        except WindowActiveError:
            pass


def get_person_status(grstate, obj):
    """
    Load status indicators if needed.
    """
    icon_list = []
    alert = grstate.config.get("options.global.status.citation-alert")
    missing = grstate.config.get("options.global.status.missing-alert")
    ranking = grstate.config.get("options.global.status.confidence-ranking")
    if alert or ranking:
        (
            alert_icon,
            rank_icon,
            rank_text,
            missing_icon,
            missing_text,
        ) = get_person_status_icons(grstate, obj)
        if ranking and rank_icon:
            icon_list.append(prepare_icon(rank_icon, tooltip=rank_text))
        if alert and alert_icon:
            icon_list.append(alert_icon)
        if missing and missing_icon:
            icon_list.append(prepare_icon(missing_icon, tooltip=missing_text))
    return icon_list


def get_person_status_icons(grstate, obj):
    """
    Evaluate and return status icons for an object.
    """
    alert_list = get_event_fields(grstate, "alert")
    alert_minimum = grstate.config.get(
        "options.global.status.citation-alert-minimum"
    )
    alert_minimum = alert_minimum + 1
    rank_list = get_event_fields(grstate, "rank")
    for event in ["Birth", "Death"]:
        if event not in rank_list:
            rank_list.append(event)
    for option in RANK_OPTIONS:
        if grstate.config.get(option):
            rank_list.append(RANK_OPTIONS[option])
    missing_list = get_event_fields(grstate, "missing", count=6)
    (
        total_rank_items,
        total_rank_confidence,
        missing_alerts,
        confidence_alerts,
    ) = get_status_ranking(
        grstate.dbstate.db,
        obj,
        rank_list,
        alert_list,
        alert_minimum,
        missing_list,
    )
    if total_rank_confidence != 0:
        rank_score = total_rank_confidence / total_rank_items
        rank_icon = RANK_ICONS.get(int(rank_score))
        rank_text = " ".join(
            (_("Confidence"), _("Ranking"), ":", str(rank_score))
        )
    else:
        rank_icon = None
        rank_text = ""

    if confidence_alerts:
        alert_icon = GrampsCitationAlertIcon(grstate, confidence_alerts)
    else:
        alert_icon = None

    if missing_alerts:
        missing_icon = "emblem-important"
        missing_text = ", ".join(tuple(missing_alerts))
        missing_text = "".join(
            (_("Missing"), " ", _("Events"), ": ", missing_text)
        )
    else:
        missing_icon = None
        missing_text = ""

    return alert_icon, rank_icon, rank_text, missing_icon, missing_text
