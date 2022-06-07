#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022   Christopher Horn
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
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Event, EventType, Family, Person
from gramps.gui.editors import EditEvent

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from view.common.common_classes import GrampsBaseIcon
from view.common.common_utils import get_confidence, prepare_icon
from view.config.config_const import (
    CONFIDENCE_LEVEL,
    OPTION_VALUE_BIRTH,
    OPTION_VALUE_BAPTISM,
    OPTION_VALUE_CHRISTENING,
    OPTION_VALUE_WILL,
    OPTION_VALUE_DEATH,
    OPTION_VALUE_BURIAL,
    OPTION_VALUE_CREMATION,
    OPTION_VALUE_PROBATE,
    OPTION_VALUE_BANNS,
    OPTION_VALUE_MARRIAGE,
    OPTION_VALUE_DIVORCE,
)

from view.config.config_utils import (
    config_event_fields,
    create_grid,
    get_event_fields,
)
from view.menus.menu_utils import menu_item, show_menu

_ = glocale.translation.sgettext

OPTION_CONFIDENCE_RANKING = "status.confidence-ranking"
OPTION_RANK_OBJECT = "status.rank-object"
OPTION_RANK_NAMES = "status.rank-names"
OPTION_RANK_EVENTS = "status.rank-events"
OPTION_RANK_ORDINANCES = "status.rank-ordinances"
OPTION_RANK_ATTRIBUTES = "status.rank-attributes"
OPTION_RANK_ASSOCIATIONS = "status.rank-associations"
OPTION_RANK_ADDRESSES = "status.rank-addresses"
OPTION_RANK_SPOUSES = "status.rank-spouses"
OPTION_RANK_CHILDREN = "status.rank-children"
OPTION_CITATION_ALERT = "status.citation-alert"
OPTION_CITATION_ALERT_EDIT = "status.citation-alert-edit"
OPTION_CITATION_ALERT_MINIMUM = "status.citation-alert-minimum"
OPTION_MISSING_ALERT = "status.missing-alert"

RANK_OPTIONS = [
    OPTION_RANK_OBJECT,
    OPTION_RANK_NAMES,
    OPTION_RANK_EVENTS,
    OPTION_RANK_ORDINANCES,
    OPTION_RANK_ATTRIBUTES,
    OPTION_RANK_ASSOCIATIONS,
    OPTION_RANK_ADDRESSES,
    OPTION_RANK_SPOUSES,
    OPTION_RANK_CHILDREN,
]

RANK_ICONS = {
    1: "non-starred",
    2: "semi-starred",
    3: "semi-starred-rtl",
    4: "starred",
}


# ------------------------------------------------------------------------
#
# Status plugin API consists of a dictionary with the supported types,
# default options, callable to build configuration grid for the options,
# and callable to check status and return any icons as needed.
#
# ------------------------------------------------------------------------
def load_on_reg(_dummy_dbstate, _dummy_uistate, _dummy_plugin):
    """
    Return status plugin attributes.
    """
    return [
        {
            "supported_types": ["Person"],
            "default_options": default_options,
            "get_config_grids": get_person_status_config_grids,
            "get_status": get_person_status,
        }
    ]


# ------------------------------------------------------------------------
#
# Default options for this status plugin
#
# ------------------------------------------------------------------------
default_options = [
    (OPTION_CONFIDENCE_RANKING, True),
    (OPTION_RANK_OBJECT, True),
    (OPTION_RANK_NAMES, True),
    (OPTION_RANK_EVENTS, True),
    (OPTION_RANK_ORDINANCES, True),
    (OPTION_RANK_ATTRIBUTES, True),
    (OPTION_RANK_ASSOCIATIONS, True),
    (OPTION_RANK_ADDRESSES, True),
    (OPTION_RANK_SPOUSES, True),
    (OPTION_RANK_CHILDREN, True),
    ("status.rank-1", OPTION_VALUE_BAPTISM),
    ("status.rank-2", OPTION_VALUE_CHRISTENING),
    ("status.rank-3", OPTION_VALUE_BANNS),
    ("status.rank-4", OPTION_VALUE_MARRIAGE),
    ("status.rank-5", OPTION_VALUE_DIVORCE),
    ("status.rank-6", OPTION_VALUE_WILL),
    ("status.rank-7", OPTION_VALUE_BURIAL),
    ("status.rank-8", OPTION_VALUE_CREMATION),
    ("status.rank-9", OPTION_VALUE_PROBATE),
    ("status.rank-10", "None"),
    ("status.rank-11", "None"),
    ("status.rank-12", "None"),
    (OPTION_CITATION_ALERT, True),
    (OPTION_CITATION_ALERT_EDIT, True),
    (OPTION_CITATION_ALERT_MINIMUM, 0),
    ("status.alert-1", OPTION_VALUE_BIRTH),
    ("status.alert-2", OPTION_VALUE_BAPTISM),
    ("status.alert-3", OPTION_VALUE_CHRISTENING),
    ("status.alert-4", OPTION_VALUE_BANNS),
    ("status.alert-5", OPTION_VALUE_MARRIAGE),
    ("status.alert-6", OPTION_VALUE_DIVORCE),
    ("status.alert-7", OPTION_VALUE_WILL),
    ("status.alert-8", OPTION_VALUE_DEATH),
    ("status.alert-9", OPTION_VALUE_BURIAL),
    ("status.alert-10", OPTION_VALUE_CREMATION),
    ("status.alert-11", OPTION_VALUE_PROBATE),
    ("status.alert-12", "None"),
    (OPTION_MISSING_ALERT, True),
    ("status.missing-1", OPTION_VALUE_BIRTH),
    ("status.missing-2", OPTION_VALUE_MARRIAGE),
    ("status.missing-3", OPTION_VALUE_DEATH),
    ("status.missing-4", OPTION_VALUE_BURIAL),
    ("status.missing-5", "None"),
    ("status.missing-6", "None"),
]


# ------------------------------------------------------------------------
#
# Function to build and return configuration grids for the options.
#
# ------------------------------------------------------------------------
def get_person_status_config_grids(configdialog, grstate, *_dummy_args):
    """
    Build status indicator configuration section.
    """
    grids = []
    grid = create_grid()
    configdialog.add_text(
        grid, _("Confidence Ranking Indicator"), 20, bold=True
    )
    configdialog.add_checkbox(
        grid,
        _("Enable confidence ranking"),
        21,
        OPTION_CONFIDENCE_RANKING,
    )
    configdialog.add_checkbox(
        grid,
        _("Include base object"),
        22,
        OPTION_RANK_OBJECT,
    )
    grid1 = create_grid()
    configdialog.add_checkbox(
        grid1,
        _("Include all names"),
        23,
        OPTION_RANK_NAMES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Include all events"),
        24,
        OPTION_RANK_EVENTS,
    )
    configdialog.add_checkbox(
        grid1,
        _("Include all ordinances"),
        25,
        OPTION_RANK_ORDINANCES,
    )
    configdialog.add_checkbox(
        grid1,
        _("Include spouses for family"),
        26,
        OPTION_RANK_SPOUSES,
    )
    grid2 = create_grid()
    configdialog.add_checkbox(
        grid2,
        _("Include all attributes"),
        23,
        OPTION_RANK_ATTRIBUTES,
        start=3,
    )
    configdialog.add_checkbox(
        grid2,
        _("Include all associations"),
        24,
        OPTION_RANK_ASSOCIATIONS,
        start=3,
    )
    configdialog.add_checkbox(
        grid2,
        _("Include all addresses"),
        25,
        OPTION_RANK_ADDRESSES,
        start=3,
    )
    configdialog.add_checkbox(
        grid2,
        _("Include children for family"),
        26,
        OPTION_RANK_CHILDREN,
        start=3,
    )
    grid.attach(grid1, 1, 24, 2, 1)
    grid.attach(grid2, 2, 24, 2, 1)
    configdialog.add_text(
        grid,
        "".join(
            (
                _(
                    "Additional Individual Events To Include "
                    "(Birth and Death Implicit)"
                ),
                ":",
            )
        ),
        25,
    )
    grid3 = config_event_fields(grstate, "rank")
    grid.attach(grid3, 1, 26, 2, 1)
    grids.append(grid)

    grid = create_grid()
    configdialog.add_text(grid, _("Citation Alert Indicator"), 50, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable citation alerts"),
        51,
        OPTION_CITATION_ALERT,
    )
    configdialog.add_combo(
        grid,
        _("Minimum confidence level required"),
        52,
        OPTION_CITATION_ALERT_MINIMUM,
        CONFIDENCE_LEVEL,
    )
    configdialog.add_checkbox(
        grid,
        _("Open event in editor instead of navigating to event page"),
        53,
        OPTION_CITATION_ALERT_EDIT,
    )
    configdialog.add_text(
        grid, "".join((_("Events Checked For Citations"), ":")), 54
    )
    grid1 = config_event_fields(grstate, "alert")
    grid.attach(grid1, 1, 55, 2, 2)
    grids.append(grid)

    grid = create_grid()
    configdialog.add_text(grid, _("Missing Event Indicator"), 60, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable missing event alerts"),
        61,
        OPTION_MISSING_ALERT,
    )
    configdialog.add_text(grid, "".join((_("Required Events"), ":")), 62)
    grid1 = config_event_fields(grstate, "missing", count=6)
    grid.attach(grid1, 1, 63, 2, 1)
    grids.append(grid)
    return grids


# ------------------------------------------------------------------------
#
# Function to check status and return icons as needed.
#
# ------------------------------------------------------------------------
def get_person_status(grstate, obj, size):
    """
    Load status indicators if needed.
    """
    icon_list = []
    alert = grstate.config.get(OPTION_CITATION_ALERT)
    missing = grstate.config.get(OPTION_MISSING_ALERT)
    ranking = grstate.config.get(OPTION_CONFIDENCE_RANKING)
    if alert or ranking:
        (
            alert_icon,
            rank_icon,
            rank_text,
            missing_icon,
            missing_text,
        ) = get_person_status_icons(grstate, obj, size)
        if ranking and rank_icon:
            icon_list.append(
                prepare_icon(rank_icon, size=size, tooltip=rank_text)
            )
        if alert and alert_icon:
            icon_list.append(alert_icon)
        if missing and missing_icon:
            icon_list.append(
                prepare_icon(missing_icon, size=size, tooltip=missing_text)
            )
    return icon_list


# ------------------------------------------------------------------------
#
# Some helper functions.
#
# ------------------------------------------------------------------------
def get_person_status_icons(grstate, obj, size):
    """
    Evaluate and return status icons for an object.
    """
    alert_list = get_event_fields(grstate, "alert")
    alert_minimum = grstate.config.get(OPTION_CITATION_ALERT_MINIMUM)
    alert_minimum = alert_minimum + 1
    rank_list = get_event_fields(grstate, "rank")
    for event in ["Birth", "Death"]:
        if event not in rank_list:
            rank_list.append(event)
    for option in RANK_OPTIONS:
        if grstate.config.get(option):
            rank_list.append(option.split("-")[1])
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
        rank_text = " ".join((_("Confidence Ranking"), ":", str(rank_score)))
    else:
        rank_icon = None
        rank_text = ""

    if confidence_alerts:
        alert_icon = GrampsCitationAlertIcon(grstate, confidence_alerts, size)
    else:
        alert_icon = None

    if missing_alerts:
        missing_icon = "emblem-important"
        missing_text = ", ".join(tuple(missing_alerts))
        missing_text = "".join((_("Missing Events"), ": ", missing_text))
    else:
        missing_icon = None
        missing_text = ""

    return alert_icon, rank_icon, rank_text, missing_icon, missing_text


def get_status_ranking(
    db,
    obj,
    rank_list=None,
    alert_list=None,
    alert_minimum=0,
    required_list=None,
):
    """
    Evaluate object attributes to collect data for confidence ranking.
    """
    rank_list = rank_list or []
    alert_list = alert_list or []
    required_list = required_list or []

    found_list = []
    missing_alerts = []
    confidence_alerts = []

    total_rank_items = 0
    total_rank_confidence = 0

    vital_count = 2
    object_bucket, events_bucket = collect_primary_object_data(
        db, obj, rank_list
    )
    for event_data in events_bucket:
        (
            event,
            event_type,
            primary,
            total_count,
            dummy_total_confidence,
            highest_confidence,
        ) = event_data
        if event_type in [EventType.BIRTH, EventType.DEATH]:
            vital_count = vital_count - 1
        event_name = event_type.xml_str()
        if primary and event_name in alert_list:
            if total_count == 0:
                confidence_alerts.append(
                    (event, "".join((str(event_type), ": ", _("Missing"))))
                )
            elif highest_confidence < alert_minimum:
                confidence_alerts.append(
                    (
                        event,
                        "".join(
                            (
                                str(event_type),
                                ": ",
                                get_confidence(highest_confidence),
                            )
                        ),
                    )
                )
        if (
            primary
            and event_name in required_list
            and event_name not in found_list
        ):
            found_list.append(event_name)

        if primary and event_name in rank_list or "events" in rank_list:
            total_rank_items = total_rank_items + 1
            total_rank_confidence = total_rank_confidence + highest_confidence

    if vital_count > 0:
        total_rank_items = total_rank_items + vital_count

    for item in required_list:
        if item not in found_list:
            missing_alerts.append(item)

    for object_data in object_bucket:
        total_rank_items = total_rank_items + 1
        total_rank_confidence = total_rank_confidence + object_data[5]

    return (
        total_rank_items,
        total_rank_confidence,
        missing_alerts,
        confidence_alerts,
    )


def collect_primary_object_data(db, obj, rank_list):
    """
    Collect all object and event data for a primary object.
    """
    buckets = ([], [])
    if isinstance(obj, Person):
        collect_person_data(db, obj, rank_list, buckets)
    elif isinstance(obj, Family):
        collect_family_data(db, obj, rank_list, buckets)
    return buckets[0], buckets[1]


def collect_person_data(db, person, rank_list, buckets, include_family=True):
    """
    Collect all citation metrics associated with a person.
    """
    (object_bucket, events_bucket) = buckets
    person_handle = person.handle

    collect_object_data(db, person, rank_list, object_bucket)
    collect_event_data(db, person, events_bucket)
    if include_family:
        if "object" in rank_list:
            for handle in person.parent_family_list:
                family = db.get_family_from_handle(handle)
                for child_ref in family.child_ref_list:
                    if child_ref.ref == person_handle:
                        collect_child_object_data(
                            db, family, _("Child"), [child_ref], object_bucket
                        )
                        break

        for handle in person.family_list:
            family = db.get_family_from_handle(handle)
            collect_object_data(db, family, rank_list, object_bucket)
            collect_event_data(db, family, events_bucket)


def collect_family_data(db, obj, rank_list, buckets, skip_handle=None):
    """
    Collect most citation metrics associated with a family.
    If requested this can include spouses and children.
    """
    (object_bucket, events_bucket) = buckets

    collect_object_data(db, obj, rank_list, object_bucket)
    collect_event_data(db, obj, events_bucket)

    get_person_from_handle = db.get_person_from_handle
    if "spouses" in rank_list:
        if obj.father_handle and obj.father_handle != skip_handle:
            father = get_person_from_handle(obj.father_handle)
            collect_person_data(
                db, father, rank_list, buckets, include_family=False
            )
        if obj.mother_handle and obj.mother_handle != skip_handle:
            mother = get_person_from_handle(obj.mother_handle)
            collect_person_data(
                db, mother, rank_list, buckets, include_family=False
            )

    if "children" in rank_list:
        for child_ref in obj.child_ref_list:
            if child_ref != skip_handle:
                child = get_person_from_handle(child_ref.ref)
                collect_person_data(
                    db, child, rank_list, buckets, include_family=False
                )


def collect_object_data(db, obj, rank_list, bucket):
    """
    Collect object citation metrics excluding their events.
    """
    person = False
    if "object" in rank_list:
        if isinstance(obj, Person):
            description = _("Person")
            person = True
        elif isinstance(obj, Family):
            description = _("Family")
        elif isinstance(obj, Event):
            description = _("Event")
        collect_child_object_data(db, obj, description, [obj], bucket)
    if person and "names" in rank_list:
        names = [obj.primary_name] + obj.alternate_names
        collect_child_object_data(db, obj, _("Name"), names, bucket)
    if "ordinances" in rank_list:
        collect_child_object_data(
            db, obj, _("Ordinance"), obj.lds_ord_list, bucket
        )
    if "attributes" in rank_list:
        collect_child_object_data(
            db, obj, _("Attribute"), obj.attribute_list, bucket
        )
    if person and "associations" in rank_list:
        collect_child_object_data(
            db, obj, _("Association"), obj.person_ref_list, bucket
        )
    if person and "addresses" in rank_list:
        collect_child_object_data(
            db, obj, _("Address"), obj.address_list, bucket
        )
    if "media" in rank_list:
        collect_child_object_data(db, obj, _("Media"), obj.media_list, bucket)


def collect_child_object_data(db, obj, description, child_list, bucket):
    """
    Collect child object citation metrics.
    """
    for child_obj in child_list:
        (
            total_count,
            total_confidence,
            highest_confidence,
        ) = get_citation_metrics(db, child_obj)
        bucket.append(
            (
                obj,
                child_obj,
                description,
                total_count,
                total_confidence,
                highest_confidence,
            )
        )


def collect_event_data(db, obj, bucket):
    """
    Collect event citation metrics.
    """
    vital_handles = get_preferred_vital_handles(obj)
    seen_list = []
    for event_ref in obj.event_ref_list:
        event = db.get_event_from_handle(event_ref.ref)
        event_type = event.get_type()
        event_name = event_type.xml_str()
        (
            total_count,
            total_confidence,
            highest_confidence,
        ) = get_citation_metrics(db, event)
        primary = False
        if event_name not in seen_list:
            if event_type in [EventType.BIRTH, EventType.DEATH]:
                if event_ref.ref in vital_handles:
                    primary = True
            else:
                primary = True
            seen_list.append(event_name)
        bucket.append(
            (
                event,
                event_type,
                primary,
                total_count,
                total_confidence,
                highest_confidence,
            )
        )


def get_preferred_vital_handles(obj):
    """
    Return list of preferred birth and death event handles.
    """
    vital_handles = []
    if isinstance(obj, Person):
        birth_ref = obj.get_birth_ref()
        if birth_ref:
            vital_handles.append(birth_ref.ref)
        death_ref = obj.get_death_ref()
        if death_ref:
            vital_handles.append(death_ref.ref)
    return vital_handles


def get_citation_metrics(db, obj):
    """
    Examine citations for an object and return what metrics are available.
    """
    total_confidence = 0
    highest_confidence = 0
    for handle in obj.citation_list:
        citation = db.get_citation_from_handle(handle)
        total_confidence = total_confidence + citation.confidence
        if citation.confidence > highest_confidence:
            highest_confidence = citation.confidence
    return len(obj.citation_list), total_confidence, highest_confidence


# ------------------------------------------------------------------------
#
# GrampsCitationAlertIcon class
#
# ------------------------------------------------------------------------
class GrampsCitationAlertIcon(GrampsBaseIcon):
    """
    A class to manage the icon and access to the citation alert items.
    """

    def __init__(self, grstate, alert_list, size):
        if len(alert_list) > 1:
            tooltip = " ".join((str(len(alert_list)), _("Citation Alerts")))
        else:
            tooltip = " ".join(("1", _("Citation Alert")))
        GrampsBaseIcon.__init__(
            self, grstate, "software-update-urgent", size=size, tooltip=tooltip
        )
        self.alert_list = alert_list

    def icon_clicked(self, event):
        """
        Build alert context menu.
        """
        menu = Gtk.Menu()
        if self.grstate.config.get(OPTION_CITATION_ALERT_EDIT):
            callback = self.edit_event
        else:
            callback = self.goto_event
        for (alert_event, alert_text) in self.alert_list:
            menu.append(
                menu_item("gramps-event", alert_text, callback, alert_event)
            )
        return show_menu(menu, self, event)

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
