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


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_children import ChildrenGrampsFrameGroup
from frame_citations import CitationsGrampsFrameGroup
from frame_couple import CoupleGrampsFrame
from frame_generic import GenericGrampsFrameGroup
from frame_media import MediaGrampsFrameGroup
from frame_notes import NotesGrampsFrameGroup
from frame_repositories import RepositoriesGrampsFrameGroup
from frame_sources import SourcesGrampsFrameGroup
from frame_timeline import TimelineGrampsFrameGroup

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


def get_generic_group(grstate, obj, framegroup, title_plural, title_single, expanded=True):
    """
    Get the group associated with a simple object.
    """
    group = framegroup(grstate, obj)
    if not group or len(group) == 0:
        return None

    text = title_plural
    if len(group) == 1:
        text = title_single

    content = Gtk.Expander(expanded=expanded, use_markup=True)
    content.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    content.add(group)
    return content

def get_children_group(grstate, family, context="child", title_plural=_("Children"), title_single=_("Child"), person=None, expanded=True):
    """
    Get the group for all the children in a family unit.
    """
    group = ChildrenGrampsFrameGroup(grstate, context, family, relation=person)
    if not group or len(group) == 0:
        return None

    text = title_plural
    if len(group) == 1:
        text = title_single

    content = Gtk.Expander(expanded=expanded, use_markup=True)
    content.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    content.add(group)
    return content

def get_family_unit(grstate, family, context="family", relation=None, vertical=None):
    """
    Get the group for a family unit.
    """
    couple = CoupleGrampsFrame(
        grstate,
        context,
        family,
        relation=relation,
    )
    expanded=grstate.config.get("{}.{}.expand-children".format(grstate.space, context))
    title_plural = _("Children")
    title_single = _("Child")
    if context == "parent":
        title_plural = _("Siblings")
        title_single = _("Sibling")

    children = get_children_group(grstate, family, context, title_plural, title_single, person=relation, expanded=expanded)
    if children and len(children) > 0:
        couple.pack_start(children, expand=True, fill=True, padding=0)
    return couple

def get_parents_group(grstate, person):
    """
    Get the group for all the parents and siblings of a person.
    """
    parents = None
    primary_handle = person.get_main_parents_family_handle()
    if primary_handle:
        parents = Gtk.Expander(expanded=True, use_markup=True)
        parents.set_label("<small><b>{}</b></small>".format(_("Parents and Siblings")))
        elements = Gtk.VBox(spacing=6)
        parents.add(elements)
        family = grstate.dbstate.db.get_family_from_handle(primary_handle)
        group = get_family_unit(grstate, family, "parent", relation=person)
        elements.add(group)

    for handle in person.parent_family_list:
        if handle != primary_handle:
            family = grstate.dbstate.db.get_family_from_handle(handle)
            group = get_family_unit(grstate, family, "parent", relation=person)
            elements.add(group)
    return parents

def get_spouses_group(grstate, person):
    """
    Get the group for all the spouses and children of a person.
    """
    spouses = None
    for handle in person.family_list:
        if spouses is None:
            spouses = Gtk.Expander(expanded=True, use_markup=True)
            spouses.set_label(
                "<small><b>{}</b></small>".format(_("Spouses and Children"))
            )
            elements = Gtk.VBox(spacing=6)
            spouses.add(elements)
        family = grstate.dbstate.db.get_family_from_handle(handle)
        group = get_family_unit(grstate, family, "spouse", relation=person)
        elements.add(group)
    return spouses

def get_citations_group(grstate, obj, sources=True):
    """
    Get the group for all the cited sources associated with an object.
    """
    if sources:
        title_plural = _("Cited Sources")
        title_single = _("Cited Source")
    else:
        title_plural = _("Citations")
        title_single = _("Citation")

    return get_generic_group(
        grstate, obj, CitationsGrampsFrameGroup,
        title_plural, title_single, expanded=True
    )

def get_timeline_group(grstate, obj, title_plural=_("Timeline Events"), title_single=_("Timeline Event")):
    """
    Get the group of timeline events associated with an object.
    """
    return get_generic_group(
        grstate, obj, TimelineGrampsFrameGroup,
        title_plural, title_single, expanded=True
    )

def get_media_group(grstate, obj, title_plural=_("Media Items"), title_single=_("Media Item")):
    """
    Get the group of media items associated with an object.
    """
    return get_generic_group(
        grstate, obj, MediaGrampsFrameGroup,
        title_plural, title_single, expanded=True
    )

def get_repositories_group(grstate, obj, title_plural=_("Repositories"), title_single=_("Repository")):
    """
    Get the group of repositories associated with an object.
    """
    return get_generic_group(
        grstate, obj, RepositoriesGrampsFrameGroup,
        title_plural, title_single, expanded=True
    )

def get_sources_group(grstate, obj, title_plural=_("Sources"), title_single=_("Source")):
    """
    Get the group of sources associated with an object.
    """
    return get_generic_group(
        grstate, obj, SourcesGrampsFrameGroup,
        title_plural, title_single, expanded=True
    )

def get_notes_group(grstate, obj, title_plural=_("Notes"), title_single=_("Note")):
    """
    Get the group of notes associated with an object.
    """
    return get_generic_group(
        grstate, obj, NotesGrampsFrameGroup,
        title_plural, title_single, expanded=True
    )

def get_references_group(grstate, obj, title_plural=_("References"), title_single=_("Reference"), maximum=0, obj_types=None, obj_list=None):
    """
    Get the group of objects that reference the given object.
    """
    if not obj_list:
        obj_list = grstate.dbstate.db.find_backlink_handles(obj.get_handle())
    if not obj_list:
        return None

    total = 0
    tuple_list = []
    if not obj_types:
        for obj in obj_list:
            tuple_list.append(obj)
            total = total + 1
    else:
        for obj_type, handle in obj_list:
            if obj_type in obj_types:
                tuple_list.append((obj_type, handle))
                total = total + 1

    not_shown = 0
    if not maximum:
        maximum = grstate.config.get("options.global.max-references-per-group")
    if total > maximum:
        not_shown = total - maximum
        tuple_list = tuple_list[:maximum]

    group = GenericGrampsFrameGroup(grstate, "Tuples", tuple_list)
    text = title_plural
    if len(group) == 1:
        text = title_single
    if not_shown:
        text = "{} ({} {})".format(text, not_shown, _("Not Shown"))

    content = Gtk.Expander(expanded=True, use_markup=True)
    content.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    content.add(group)
    return content
