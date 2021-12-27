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
GrampsFrameGroup builder functions
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
from ..frames.frame_couple import CoupleGrampsFrame
from .group_children import ChildrenGrampsFrameGroup
from .group_const import GRAMPS_GROUPS
from .group_events import EventsGrampsFrameGroup
from .group_expander import GrampsFrameGroupExpander
from .group_generic import GenericGrampsFrameGroup

_ = glocale.translation.sgettext


def group_builder(grstate, group_type, obj, args):
    """
    Generate and return group for a given object.
    """
    if group_type in GRAMPS_GROUPS:
        group = build_simple_group(grstate, group_type, obj, args)
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
    framegroup, single, plural = GRAMPS_GROUPS[group_type]
    if group_type == "timeline":
        if "page_type" in args:
            page_type = args["page_type"]
        else:
            page_type = "other"
        groptions = GrampsOptions("".join(("options.timeline.", page_type)))
        groptions.set_context("timeline")
    else:
        groptions = GrampsOptions("".join(("options.group.", group_type)))

    if "age_base" in args and args["age_base"]:
        groptions.set_age_base(args["age_base"])

    if "sources" in args and args["sources"]:
        single, plural = _("Cited Source"), _("Cited Sources")

    if "title" in args and args["title"]:
        groptions.title = args["title"]

    group = framegroup(grstate, groptions, obj)
    if not group or len(group) == 0:
        return None
    if "raw" in args and args["raw"]:
        return group
    return group_wrapper(grstate, group, (single, plural, None))


def group_wrapper(grstate, group, title):
    """
    Wrap a frame group widget with an expander.
    """
    group_title = get_group_title(group, title)
    content = GrampsFrameGroupExpander(grstate)
    content.set_label("".join(("<small><b>", group_title, "</b></small>")))
    content.add(group)
    return content


def get_group_title(group, title):
    """
    Build title for a frame group.
    """
    (single, plural, fixed) = title
    group_title = fixed
    if not group_title:
        if len(group) == 1:
            group_title = " ".join(("1", single))
        else:
            group_title = " ".join((str(len(group)), plural))
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
    groptions = GrampsOptions("".join(("options.group.", context)))
    groptions.set_relation(person)
    groptions.set_context(context)
    if "title" in args and args["title"]:
        groptions.title = args["title"]
    group = ChildrenGrampsFrameGroup(grstate, groptions, family)
    if not group or len(group) == 0:
        return None
    if "raw" in args and args["raw"]:
        return group
    if context == "parent":
        title_tuple = (_("Sibling"), _("Siblings"), None)
    else:
        title_tuple = (_("Child"), _("Children"), None)
    return group_wrapper(grstate, group, title_tuple)


def get_family_unit(grstate, family, args, context="family", relation=None):
    """
    Get the group for a family unit.
    """
    groptions = GrampsOptions("".join(("options.group.", context)))
    groptions.set_relation(relation)
    if "title" in args and args["title"]:
        groptions.title = args["title"]
    couple = CoupleGrampsFrame(
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
        couple.pack_start(children, expand=True, fill=True, padding=0)
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
            groptions = GrampsOptions("options.group.parent")
            groptions.set_context("parent")
            parents = GrampsFrameGroupExpander(
                grstate, expanded=True, use_markup=True
            )
            parents.set_label(
                "".join(
                    ("<small><b>", _("Parents and Siblings"), "</b></small>")
                )
            )
            parents.add(elements)
        else:
            parents = elements
        family = grstate.fetch("Family", primary_handle)
        group = get_family_unit(
            grstate, family, args, context="parent", relation=person
        )
        elements.add(group)

    for handle in person.parent_family_list:
        if handle != primary_handle:
            family = grstate.fetch("Family", handle)
            group = get_family_unit(
                grstate, family, args, context="parent", relation=person
            )
            elements.add(group)
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
                groptions = GrampsOptions("options.group.spouse")
                groptions.set_context("spouse")
                spouses = GrampsFrameGroupExpander(
                    grstate, expanded=True, use_markup=True
                )
                spouses.set_label(
                    "".join(
                        (
                            "<small><b>",
                            _("Spouses and Children"),
                            "</b></small>",
                        )
                    )
                )
                spouses.add(elements)
            else:
                spouses = elements
        family = grstate.fetch("Family", handle)
        group = get_family_unit(
            grstate, family, args, context="spouse", relation=person
        )
        elements.add(group)
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
        obj_list = grstate.dbstate.db.find_backlink_handles(obj.get_handle())
        if not obj_list:
            return None

    total, tuple_list = prepare_reference_items(obj_types, obj_list)
    not_shown = 0
    if not maximum:
        maximum = grstate.config.get("options.global.max.references-per-group")
    if total > maximum:
        not_shown = total - maximum
        tuple_list = tuple_list[:maximum]

    groptions = prepare_reference_options(groptions, args)
    group = GenericGrampsFrameGroup(grstate, groptions, "Tuples", tuple_list)

    single, plural = _("Reference"), _("References")
    if args and "title" in args:
        (single, plural) = args["title"]
    title = get_group_title(group, (single, plural, None))
    if not_shown:
        title = "".join(
            (title, " (", str(not_shown), " ", _("Not Shown"), ")")
        )
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
    groptions = groptions or GrampsOptions("options.group.reference")
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

        for handle in obj.get_family_handle_list():
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
    if not obj.get_event_ref_list():
        return None

    groptions = GrampsOptions("options.group.event")
    groptions.set_context("event")
    if "age_base" in args and args["age_base"]:
        groptions.set_age_base(args["age_base"])
    if "title" in args and args["title"]:
        groptions.title = args["title"]
    group = EventsGrampsFrameGroup(grstate, groptions, obj)
    elements = Gtk.VBox(spacing=6)
    elements.add(group)

    if obj_type == "Person":
        event_type = _("Personal")
    else:
        event_type = _("Family")

    if len(group) == 1:
        title = " ".join(("1", event_type, _("Event")))
    else:
        title = " ".join((str(len(group)), event_type, _("Events")))
    return group_wrapper(grstate, elements, (None, None, title))
