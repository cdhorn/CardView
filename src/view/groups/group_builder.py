#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022  Christopher Horn
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
CardGroup builder functions
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
from gramps.gen.lib import Family, Person

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..cards import FamilyCard
from .group_children import ChildrenCardGroup
from .group_const import GENERIC_GROUPS, STATISTICS_GROUPS
from .group_events import EventsCardGroup
from .group_expander import CardGroupExpander
from .group_generic import GenericCardGroup
from .group_statistics import StatisticsCardGroup

_ = glocale.translation.sgettext


def group_builder(grstate, group_type, obj, args):
    """
    Generate and return group for a given object.
    """
    if group_type in GENERIC_GROUPS:
        group = build_simple_group(grstate, group_type, obj, args)
    elif group_type in STATISTICS_GROUPS:
        group = build_statistics_group(grstate, group_type)
    elif group_type == "event":
        group = get_events_group(grstate, obj, args)
    elif group_type == "parent":
        group = get_parents_group(grstate, obj, args)
    elif group_type == "spouse":
        group = get_spouses_group(grstate, obj, args)
    elif group_type == "child":
        group = get_children_group(grstate, obj, args)
    elif group_type == "reference":
        group = get_references_group(grstate, obj, args)
    else:
        group = None
    return group


def build_simple_group(grstate, group_type, obj, args):
    """
    Generate and return a simple group for a given object.
    """
    args = args or {}
    cardgroup, single, plural = GENERIC_GROUPS[group_type]
    if group_type == "timeline":
        if "page_type" in args:
            page_type = args["page_type"]
        else:
            page_type = "other"
        groptions = GrampsOptions("timeline.%s" % page_type)
        groptions.set_context("timeline")
    else:
        groptions = GrampsOptions("group.%s" % group_type)

    if "age_base" in args and args["age_base"]:
        groptions.set_age_base(args["age_base"])

    if "sources" in args and args["sources"]:
        single, plural = _("Cited Source"), _("Cited Sources")

    if "title" in args and args["title"]:
        groptions.title = args["title"]

    group = cardgroup(grstate, groptions, obj)
    if not group or len(group) == 0:
        return None
    if "raw" in args and args["raw"]:
        return group
    return group_wrapper(grstate, group, (single, plural, None))


def build_statistics_group(grstate, group):
    """
    Generate and return a database statistics group.
    """
    title = STATISTICS_GROUPS[group]
    groptions = GrampsOptions("group.%s" % group)
    group = StatisticsCardGroup(grstate, groptions, group)
    return group_wrapper(grstate, group, (title, title, title))


def group_wrapper(grstate, group, title, force_mode=-1):
    """
    Wrap a card group widget with an expander.
    """
    group_title = get_group_title(group, title)
    mode = grstate.config.get("display.group-mode")
    if force_mode > -1:
        mode = force_mode
    if mode in [0, 1, 2]:
        label = Gtk.Label(
            use_markup=True,
            label="<small><b> %s</b></small>" % group_title,
            vexpand=False,
        )
        if mode == 0:
            label.set_xalign(0.0)
        elif mode == 2:
            label.set_xalign(1.0)
        vbox = Gtk.VBox(vexpand=False, hexpand=False)
        vbox.pack_start(label, False, False, 0)
        vbox.pack_start(group, False, False, 0)
        return vbox
    content = CardGroupExpander(grstate, mode == 4)
    content.set_label("<small><b>%s</b></small>" % group_title)
    content.add(group)
    return content


def get_group_title(group, title):
    """
    Build title for a card group.
    """
    (single, plural, fixed) = title
    group_title = fixed
    if not group_title:
        if len(group) == 1:
            group_title = "1 %s" % single
        else:
            group_title = "%s %s" % (str(len(group)), plural)
    return group_title


def get_children_group(
    grstate,
    family,
    args,
    context="child",
    person=None,
):
    """
    Get the group for all the children in a family unit.
    """
    groptions = GrampsOptions("group.%s" % context)
    groptions.set_relation(person)
    groptions.set_context(context)
    if "title" in args and args["title"]:
        groptions.title = args["title"]
    group = ChildrenCardGroup(grstate, groptions, family)
    if not group or len(group) == 0:
        return None
    if "raw" in args and args["raw"]:
        return group
    if context == "parent":
        title_tuple = (_("Sibling"), _("Siblings"), None)
    else:
        title_tuple = (_("Child"), _("Children"), None)
    return group_wrapper(grstate, group, title_tuple, force_mode=3)


def get_family_unit(grstate, family, args, context="family", relation=None):
    """
    Get the group for a family unit.
    """
    groptions = GrampsOptions("group.%s" % context)
    groptions.set_relation(relation)
    if "title" in args and args["title"]:
        groptions.title = args["title"]
    couple = FamilyCard(
        grstate,
        groptions,
        family,
    )
    children = get_children_group(
        grstate,
        family,
        args,
        context=context,
        person=relation,
    )
    if children and len(children) > 0:
        couple.pack_start(children, expand=False, fill=False, padding=0)
    return couple


def get_parents_group(grstate, person, args):
    """
    Get the group for all the parents and siblings of a person.
    """
    parents = None
    primary_handle = person.get_main_parents_family_handle()
    if primary_handle:
        elements = Gtk.VBox(spacing=6)
        if "raw" not in args or not args["raw"]:
            groptions = GrampsOptions("group.parent")
            groptions.set_context("parent")
            title = _("Parents and Siblings")
            parents = group_wrapper(grstate, elements, (title, title, title))
        else:
            parents = elements
        family = grstate.fetch("Family", primary_handle)
        group = get_family_unit(
            grstate, family, args, context="parent", relation=person
        )
        elements.pack_start(group, expand=False, fill=False, padding=0)

    for handle in person.parent_family_list:
        if handle != primary_handle:
            family = grstate.fetch("Family", handle)
            group = get_family_unit(
                grstate, family, args, context="parent", relation=person
            )
            elements.pack_start(group, expand=False, fill=False, padding=0)
    return parents


def get_spouses_group(grstate, person, args):
    """
    Get the group for all the spouses and children of a person.
    """
    spouses = None
    for handle in person.family_list:
        if spouses is None:
            elements = Gtk.VBox(spacing=6)
            if "raw" not in args or not args["raw"]:
                groptions = GrampsOptions("group.spouse")
                groptions.set_context("spouse")
                title = _("Spouses and Children")
                spouses = group_wrapper(
                    grstate, elements, (title, title, title)
                )
            else:
                spouses = elements
        family = grstate.fetch("Family", handle)
        group = get_family_unit(
            grstate, family, args, context="spouse", relation=person
        )
        elements.pack_start(group, expand=False, fill=False, padding=0)
    return spouses


def get_references_group(
    grstate,
    obj,
    args,
    groptions=None,
    maximum=0,
    obj_types=None,
    obj_list=None,
):
    """
    Get the group of objects that reference the given object.
    """
    if not obj_list:
        obj_list = grstate.dbstate.db.find_backlink_handles(obj.handle)
        if not obj_list:
            return None

    total, tuple_list = prepare_reference_items(obj_types, obj_list)
    not_shown = 0
    if not maximum:
        maximum = grstate.config.get("general.references-max-per-group")
    if total > maximum:
        not_shown = total - maximum
        tuple_list = tuple_list[:maximum]

    groptions = prepare_reference_options(groptions, args)
    group = GenericCardGroup(grstate, groptions, "Tuples", tuple_list)

    single, plural = _("Reference"), _("References")
    if args and "title" in args:
        (single, plural) = args["title"]
    title = get_group_title(group, (single, plural, None))
    if not_shown:
        title = "%s (%s %s)" % (title, str(not_shown), _("Not Shown"))
    return group_wrapper(grstate, group, (None, None, title))


def prepare_reference_items(obj_types, obj_list):
    """
    Prepare sorted item list.
    """
    total = 0
    tuple_list = []
    handle_cache = []
    if not obj_types:
        for item in obj_list:
            if item[1] not in handle_cache:
                tuple_list.append(item)
                handle_cache.append(item[1])
                total = total + 1
    else:
        for obj_type, handle in obj_list:
            if obj_type in obj_types and handle not in handle_cache:
                tuple_list.append((obj_type, handle))
                handle_cache.append(handle)
                total = total + 1
    del handle_cache
    tuple_list.sort(key=lambda x: x[0])
    return total, tuple_list


def prepare_reference_options(groptions, args):
    """
    Prepare references options.
    """
    groptions = groptions or GrampsOptions("group.reference")
    if args and "age_base" in args and args["age_base"]:
        groptions.set_age_base(args["age_base"])
    if args and "title" in args and args["title"]:
        groptions.title = args["title"]
    return groptions


def get_events_group(grstate, obj, args):
    """
    Get the group for all the events related to a person or family
    """
    group_set = Gtk.VBox(spacing=6, vexpand=False)
    if isinstance(obj, Person):
        group = prepare_event_group(grstate, obj, "Person", args)
        if group:
            group_set.pack_start(group, False, True, 0)

        for handle in obj.family_list:
            family = grstate.fetch("Family", handle)
            group = prepare_event_group(grstate, family, "Family", args)
            if group:
                group_set.pack_start(group, False, True, 0)
    elif isinstance(obj, Family):
        group = prepare_event_group(grstate, obj, "Family", args)
        if group:
            group_set.pack_start(group, False, True, 0)
    return group_set


def prepare_event_group(grstate, obj, obj_type, args):
    """
    Prepare and return an event group for use in a group set.
    """
    if not obj.event_ref_list:
        return None

    groptions = GrampsOptions("group.event")
    groptions.set_context("event")
    if "age_base" in args and args["age_base"]:
        groptions.set_age_base(args["age_base"])
    if "title" in args and args["title"]:
        groptions.title = args["title"]
    group = EventsCardGroup(grstate, groptions, obj)
    elements = Gtk.VBox(spacing=6)
    elements.add(group)

    if obj_type == "Person":
        event_type = _("Personal")
    else:
        event_type = _("Family")

    if len(group) == 1:
        title = "1 %s %s" % (event_type, _("Event"))
    else:
        title = "%s %s %s" % (str(len(group)), event_type, _("Events"))
    return group_wrapper(grstate, elements, (None, None, title))
