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
Base field building functions
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import HandleError

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_const import (
    _BIRTH_EQUIVALENTS,
    _DEATH_EQUIVALENTS,
    _DIVORCE_EQUIVALENTS,
    _MARRIAGE_EQUIVALENTS,
)
from ..common.common_vitals import get_relation
from .field_utils import get_event_labels

_ = glocale.translation.sgettext


def get_event_field(grstate, obj, event_type, args):
    """
    Find an event and return the date and place.
    """
    args = args or {}
    skip_birth = args.get("skip_birth_alternates")
    have_birth = args.get("have_birth")
    skip_death = args.get("skip_death_alternates")
    have_death = args.get("have_death")
    skip_marriage = args.get("skip_marriage_alternates")
    have_marriage = args.get("have_marriage")
    skip_divorce = args.get("skip_divorce_alternates")
    have_divorce = args.get("have_divorce")
    event_cache = args.get("event_cache") or {}
    for event in event_cache:
        if event.get_type().xml_str() == event_type:
            if skip_birth and have_birth:
                if event_type in _BIRTH_EQUIVALENTS:
                    return []
            if skip_death and have_death:
                if event_type in _DEATH_EQUIVALENTS:
                    return []
            if skip_marriage and have_marriage:
                if event_type in _MARRIAGE_EQUIVALENTS:
                    return []
            if skip_divorce and have_divorce:
                if event_type in _DIVORCE_EQUIVALENTS:
                    return []
            return get_event_labels(grstate, event, args)
    return []


def get_fact_field(grstate, obj, event_type, args):
    """
    Find an event and return the description.
    """
    args = args or {}
    get_link = args.get("get_link")
    assert get_link is not None
    event_cache = args.get("event_cache") or {}
    for event in event_cache:
        if event.get_type().xml_str() == event_type:
            if event.get_description():
                label = get_link(
                    str(event.get_type()),
                    "Event",
                    event.get_handle(),
                    title=False,
                )
                value = get_link(
                    event.get_description(),
                    "Event",
                    event.get_handle(),
                    title=False,
                )
                return [(label, value)]
    return []


def get_attribute_field(grstate, obj, attribute_type, args):
    """
    Find an attribute and return field data.
    """
    args = args or {}
    get_label = args.get("get_label")
    assert get_label is not None
    skip_labels = args.get("skip_labels")
    for attribute in obj.get_attribute_list():
        if attribute.get_type().xml_str() == attribute_type:
            if attribute.get_value():
                value = get_label(attribute.get_value())
                if skip_labels:
                    return [(value, get_label(""))]
                label = get_label(str(attribute.get_type()))
                return [(label, value)]
    return []


def get_relation_field(grstate, obj, relation_handle, args):
    """
    Calculate and return relation field data.
    """
    args = args or {}
    get_label = args.get("get_label")
    assert get_label is not None
    get_link = args.get("get_link")
    assert get_link is not None
    label = get_label(_("Relation"))

    if obj.get_handle() == relation_handle:
        value = get_label(_("Home person"))
    else:
        try:
            relation = grstate.fetch("Person", relation_handle)
            relationship = get_relation(
                grstate.dbstate.db,
                obj,
                relation,
                depth=global_config.get("behavior.generation-depth"),
            )
            if relationship:
                text = relationship.title()
            else:
                text = " ".join(
                    (_("Not related to"), name_displayer.display(relation))
                )
            value = get_link(
                text,
                "Person",
                relation_handle,
                title=False,
            )
        except HandleError:
            value = get_label(
                "".join(("[", _("Missing"), " ", _("Person"), "]"))
            )
    return [(label, value)]
