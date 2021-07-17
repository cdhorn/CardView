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
from frame_couple import CoupleGrampsFrame
from frame_media import MediaGrampsFrameGroup
from frame_sources import SourcesGrampsFrameGroup
from frame_timeline import TimelineGrampsFrameGroup

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


def get_parents_group(dbstate, uistate, person, router, config=None, defaults=None):
    """
    Get all the parents and siblings for a person.
    """
    parents = None
    primary_handle = person.get_main_parents_family_handle()
    if primary_handle:
        parents = Gtk.Expander(expanded=True, use_markup=True)
        parents.set_label("<small><b>{}</b></small>".format(_("Parents and Siblings")))
        elements = Gtk.VBox(spacing=6)
        parents.add(elements)

        family = dbstate.db.get_family_from_handle(primary_handle)
        couple = CoupleGrampsFrame(
            dbstate,
            uistate,
            router,
            family,
            "parent",
            "preferences.profile.person",
            config,
            relation=person,
            defaults=defaults
        )
        children = ChildrenGrampsFrameGroup(
            dbstate,
            uistate,
            router,
            family,
            "parent",
            "preferences.profile.person",
            config,
            relation=person,
            defaults=defaults
        )
        if children.number > 0:
            expander = Gtk.Expander(
                expand=True,
                use_markup=True,
                expanded=config.get(
                    "preferences.profile.person.parent.expand-children"
                ),
            )
            expander.add(children)
            expander.set_label(
                "<b><small>{} {}</small></b>".format(children.number, _("Siblings"))
            )
            couple.pack_start(expander, expand=True, fill=True, padding=0)
        elements.add(couple)

    for handle in person.parent_family_list:
        if handle != primary_handle:
            family = dbstate.db.get_family_from_handle(handle)
            couple = CoupleGrampsFrame(
                dbstate,
                uistate,
                router,
                family,
                "parent",
                "preferences.profile.person",
                config,
                relation=person,
                defaults=defaults
            )
            children = ChildrenGrampsFrameGroup(
                dbstate,
                uistate,
                router,
                family,
                "parent",
                "preferences.profile.person",
                config,
                relation=person,
                defaults=defaults
            )
            if children.number > 0:
                expander = Gtk.Expander(
                    expand=True,
                    use_markup=True,
                    expanded=config.get(
                        "preferences.profile.person.parent.expand-children"
                    ),
                )
                expander.add(children)
                expander.set_label(
                    "<b><small>{} {}</small></b>".format(children.number, _("Siblings"))
                )
                couple.pack_start(expander, expand=True, fill=True, padding=0)
            elements.add(couple)
    return parents

def get_spouses_group(dbstate, uistate, person, router, config=None, defaults=None):
    """
    Get all the spouses and children for a person.
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
        family = dbstate.db.get_family_from_handle(handle)
        couple = CoupleGrampsFrame(
            dbstate,
            uistate,
            router,
            family,
            "spouse",
            "preferences.profile.person",
            config,
            relation=person,
            parent=person,
            defaults=defaults
        )
        children = ChildrenGrampsFrameGroup(
            dbstate,
            uistate,
            router,
            family,
            "spouse",
            "preferences.profile.person",
            config,
            relation=person,
            defaults=defaults
        )
        if children.number > 0:
            expander = Gtk.Expander(
                expand=True,
                use_markup=True,
                expanded=config.get(
                    "preferences.profile.person.spouse.expand-children"
                ),
            )
            expander.add(children)
            expander.set_label(
                "<b><small>{} {}</small></b>".format(children.number, _("Children"))
            )
            couple.pack_start(expander, expand=True, fill=True, padding=0)
        elements.pack_start(couple, True, True, 0)
    return spouses

def get_citation_group(dbstate, uistate, obj, router, space, config, sources=True):
    """
    Get all the cited sources associated with an object.
    """
    group = SourcesGrampsFrameGroup(dbstate, uistate, router, obj, space, config)
    if len(group) == 0:
        return None

    if sources:
        text = _("Cited Sources")
        if len(group) == 1:
            text = _("Cited Source")
    else:
        text = _("Citations")
        if len(group) == 1:
            text = _("Citation")

    sources = Gtk.Expander(expanded=True, use_markup=True)
    sources.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    sources.add(group)
    return sources

def get_timeline_group(dbstate, uistate, obj, router, config=None, space="preferences.profile.person", title=None):
    """
    Get a timeline of events associated with an object.
    """
    group = TimelineGrampsFrameGroup(dbstate, uistate, router, obj, config=config, space=space)
    if not group.count:
        return None

    text = _("Timeline Events")
    if len(group) == 1:
        text = _("Timeline Event")
    if title:
        text = title

    timeline = Gtk.Expander(expanded=True, use_markup=True)
    timeline.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    timeline.add(group)
    return timeline

def get_media_group(dbstate, uistate, obj, router, space, config, title=None):
    """
    Get all the media items associated with an object.
    """
    group = MediaGrampsFrameGroup(dbstate, uistate, router, obj, space, config)
    if len(group) == 0:
        return None

    text = _("Media Items")
    if len(group) == 1:
        text = _("Media Item")
    if title:
        text = title

    media = Gtk.Expander(expanded=True, use_markup=True)
    media.set_label("<small><b>{} {}</b></small>".format(len(group), text))
    media.add(group)
    return media
