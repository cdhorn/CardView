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
Routines to prepare object groups
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
from gramps.gen.lib import Person, Family

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..frames.frame_couple import CoupleGrampsFrame
from .group_addresses import AddressesGrampsFrameGroup
from .group_associations import AssociationsGrampsFrameGroup
from .group_attributes import AttributesGrampsFrameGroup
from .group_children import ChildrenGrampsFrameGroup
from .group_citations import CitationsGrampsFrameGroup
from .group_classes import GrampsFrameGroupExpander
from .group_events import EventsGrampsFrameGroup
from .group_generic import GenericGrampsFrameGroup
from .group_media import MediaGrampsFrameGroup
from .group_names import NamesGrampsFrameGroup
from .group_notes import NotesGrampsFrameGroup
from .group_ordinances import LDSOrdinancesGrampsFrameGroup
from .group_repositories import RepositoriesGrampsFrameGroup
from .group_sources import SourcesGrampsFrameGroup
from .group_timeline import TimelineGrampsFrameGroup
from .group_urls import UrlsGrampsFrameGroup

_ = glocale.translation.sgettext


def get_generic_group(
    grstate,
    groptions,
    obj,
    framegroup,
    title_plural,
    title_single,
    expanded=True,
    raw=False,
):
    """
    Get the group associated with a simple object.
    """
    group = framegroup(grstate, groptions, obj)
    if not group or len(group) == 0:
        return None

    if raw:
        return group

    text = title_plural
    if len(group) == 1:
        text = title_single

    content = GrampsFrameGroupExpander(
        grstate, groptions, expanded=expanded, use_markup=True
    )
    content.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    content.add(group)
    return content


def get_children_group(
    grstate,
    family,
    context="child",
    title_plural=_("Children"),
    title_single=_("Child"),
    person=None,
    expanded=True,
    raw=False,
    age_base=None,
):
    """
    Get the group for all the children in a family unit.
    """
    groptions = GrampsOptions("options.group.{}".format(context))
    groptions.set_relation(person)
    groptions.set_context(context)
    group = ChildrenGrampsFrameGroup(grstate, groptions, family)
    if not group or len(group) == 0:
        return None

    if raw:
        return group

    text = title_plural
    if len(group) == 1:
        text = title_single

    content = GrampsFrameGroupExpander(
        grstate, groptions, expanded=expanded, use_markup=True
    )
    content.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    content.add(group)
    return content


def get_family_unit(
    grstate, family, context="family", relation=None, raw=False, age_base=None
):
    """
    Get the group for a family unit.
    """
    groptions = GrampsOptions("options.group.{}".format(context))
    groptions.set_relation(relation)
    couple = CoupleGrampsFrame(
        grstate,
        groptions,
        family,
    )
    if raw:
        expanded = True
    else:
        expanded = grstate.config.get(
            "options.group.{}.expand-children".format(context)
        )
    title_plural = _("Children")
    title_single = _("Child")
    if context == "parent":
        title_plural = _("Siblings")
        title_single = _("Sibling")

    children = get_children_group(
        grstate,
        family,
        context,
        title_plural,
        title_single,
        person=relation,
        expanded=expanded,
    )
    if children and len(children) > 0:
        couple.pack_start(children, expand=True, fill=True, padding=0)
    return couple


def get_parents_group(grstate, person, raw=False, age_base=None):
    """
    Get the group for all the parents and siblings of a person.
    """
    parents = None
    primary_handle = person.get_main_parents_family_handle()
    if primary_handle:
        elements = Gtk.VBox(spacing=6)
        if not raw:
            groptions = GrampsOptions("options.group.parent")
            groptions.set_context("parent")
            parents = GrampsFrameGroupExpander(
                grstate, groptions, expanded=True, use_markup=True
            )
            parents.set_label(
                "<small><b>{}</b></small>".format(_("Parents and Siblings"))
            )
            parents.add(elements)
        else:
            parents = elements
        family = grstate.fetch("Family", primary_handle)
        group = get_family_unit(
            grstate, family, "parent", relation=person, raw=raw
        )
        elements.add(group)

    for handle in person.parent_family_list:
        if handle != primary_handle:
            family = grstate.fetch("Family", handle)
            group = get_family_unit(
                grstate, family, "parent", relation=person, raw=raw
            )
            elements.add(group)
    return parents


def get_spouses_group(grstate, person, raw=False, age_base=None):
    """
    Get the group for all the spouses and children of a person.
    """
    spouses = None
    for handle in person.family_list:
        if spouses is None:
            elements = Gtk.VBox(spacing=6)
            if not raw:
                groptions = GrampsOptions("options.group.spouse")
                groptions.set_context("spouse")
                spouses = GrampsFrameGroupExpander(
                    grstate, groptions, expanded=True, use_markup=True
                )
                spouses.set_label(
                    "<small><b>{}</b></small>".format(
                        _("Spouses and Children")
                    )
                )
                spouses.add(elements)
            else:
                spouses = elements
        family = grstate.fetch("Family", handle)
        group = get_family_unit(
            grstate, family, "spouse", relation=person, raw=raw
        )
        elements.add(group)
    return spouses


def get_citations_group(grstate, obj, sources=True, raw=False, age_base=None):
    """
    Get the group for all the cited sources associated with an object.
    """
    if sources:
        title_plural = _("Cited Sources")
        title_single = _("Cited Source")
    else:
        title_plural = _("Citations")
        title_single = _("Citation")

    groptions = GrampsOptions("options.group.citation")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        CitationsGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_timeline_group(
    grstate,
    obj,
    title_plural=_("Timeline Events"),
    title_single=_("Timeline Event"),
    raw=False,
    age_base=None,
):
    """
    Get the group of timeline events associated with an object.
    """
    groptions = GrampsOptions("options.timeline.{}".format(grstate.page_type))
    groptions.set_context("timeline")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        TimelineGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_media_group(
    grstate,
    obj,
    title_plural=_("Media Items"),
    title_single=_("Media Item"),
    raw=False,
    age_base=None,
):
    """
    Get the group of media items associated with an object.
    """
    groptions = GrampsOptions("options.group.media")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        MediaGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_repositories_group(
    grstate,
    obj,
    title_plural=_("Repositories"),
    title_single=_("Repository"),
    raw=False,
    age_base=None,
):
    """
    Get the group of repositories associated with an object.
    """
    groptions = GrampsOptions("options.group.repository")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        RepositoriesGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_sources_group(
    grstate,
    obj,
    title_plural=_("Sources"),
    title_single=_("Source"),
    raw=False,
    age_base=None,
):
    """
    Get the group of sources associated with an object.
    """
    groptions = GrampsOptions("options.group.source")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        SourcesGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_notes_group(
    grstate,
    obj,
    title_plural=_("Notes"),
    title_single=_("Note"),
    raw=False,
    age_base=None,
):
    """
    Get the group of notes associated with an object.
    """
    groptions = GrampsOptions("options.group.note")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        NotesGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_references_group(
    grstate,
    obj,
    groptions=None,
    title_plural=_("References"),
    title_single=_("Reference"),
    maximum=0,
    obj_types=None,
    obj_list=None,
    age_base=None,
):
    """
    Get the group of objects that reference the given object.
    """
    if not obj_list:
        obj_list = grstate.dbstate.db.find_backlink_handles(obj.get_handle())
    if not obj_list:
        return None

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
            if obj_type in obj_types:
                if handle not in handle_cache:
                    tuple_list.append((obj_type, handle))
                    handle_cache.append(handle)
                    total = total + 1
    del handle_cache
    tuple_list.sort(key=lambda x: x[0])

    not_shown = 0
    if not maximum:
        maximum = grstate.config.get("options.global.max-references-per-group")
    if total > maximum:
        not_shown = total - maximum
        tuple_list = tuple_list[:maximum]

    groptions = groptions or GrampsOptions("options.group.reference")
    groptions.set_age_base(age_base)
    group = GenericGrampsFrameGroup(grstate, groptions, "Tuples", tuple_list)
    text = title_plural
    if len(group) == 1:
        text = title_single
    if not_shown:
        text = "{} ({} {})".format(text, not_shown, _("Not Shown"))

    content = GrampsFrameGroupExpander(
        grstate, groptions, expanded=True, use_markup=True
    )
    content.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    content.add(group)
    return content


def get_associations_group(
    grstate,
    obj,
    title_plural=_("Associations"),
    title_single=_("Association"),
    raw=False,
    age_base=None,
):
    """
    Get the group of associations associated with a person.
    """
    groptions = GrampsOptions("options.group.association")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        AssociationsGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_addresses_group(
    grstate,
    obj,
    title_plural=_("Addresses"),
    title_single=_("Address"),
    raw=False,
    age_base=None,
):
    """
    Get the group of addresses associated with an object.
    """
    groptions = GrampsOptions("options.group.address")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        AddressesGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_attributes_group(
    grstate,
    obj,
    title_plural=_("Attributes"),
    title_single=_("Attribute"),
    raw=False,
    age_base=None,
):
    """
    Get the group of attributes associated with an object.
    """
    groptions = GrampsOptions("options.group.attribute")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        AttributesGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_names_group(
    grstate,
    obj,
    title_plural=_("Names"),
    title_single=_("Name"),
    raw=False,
    age_base=None,
):
    """
    Get the group of names associated with an object.
    """
    groptions = GrampsOptions("options.group.name")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        NamesGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_urls_group(
    grstate,
    obj,
    title_plural=_("Urls"),
    title_single=_("Url"),
    raw=False,
    age_base=None,
):
    """
    Get the group of urls associated with an object.
    """
    groptions = GrampsOptions("options.group.url")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        UrlsGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_ordinances_group(
    grstate,
    obj,
    title_plural=_("Ordinances"),
    title_single=_("Ordinance"),
    age_base=None,
    raw=False,
):
    """
    Get the group of ordinances associated with an object.
    """
    groptions = GrampsOptions("options.group.ldsord")
    return get_generic_group(
        grstate,
        groptions,
        obj,
        LDSOrdinancesGrampsFrameGroup,
        title_plural,
        title_single,
        expanded=True,
        raw=raw,
    )


def get_events_group(grstate, obj, raw=False, age_base=None):
    """
    Get the group for all the events related to a person or family
    """
    group_set = Gtk.VBox(spacing=6)

    if isinstance(obj, Person):
        group = prepare_event_group(grstate, obj, "Person")
        if group:
            group_set.add(group)

        for handle in obj.get_family_handle_list():
            family = grstate.fetch("Family", handle)
            group = prepare_event_group(grstate, family, "Family")
            if group:
                group_set.add(group)
    elif isinstance(obj, Family):
        group = prepare_event_group(grstate, obj, "Family")
        if group:
            group_set.add(group)
    return group_set


def prepare_event_group(grstate, obj, obj_type):
    """
    Prepare and return an event group for use in a group set.
    """
    if not obj.get_event_ref_list():
        return None

    groptions = GrampsOptions("options.group.event")
    groptions.set_context("event")
    group = EventsGrampsFrameGroup(grstate, groptions, obj)
    elements = Gtk.VBox(spacing=6)
    elements.add(group)

    if obj_type == "Person":
        event_type = _("Personal")
    else:
        event_type = _("Family")

    if len(group) == 1:
        title = "1 {} {}".format(event_type, _("Event"))
    else:
        title = "{} {} {}".format(len(group), event_type, _("Events"))

    header = GrampsFrameGroupExpander(
        grstate, groptions, expanded=True, use_markup=True
    )
    header.set_label("<small><b>{}</b></small>".format(title))
    header.add(elements)
    return header
