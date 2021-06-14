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
Placard utility functions.
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
from frame_citation import CitationProfileFrame
from frame_children import ChildrenProfileFrame
from frame_couple import CoupleProfileFrame
from frame_timeline import generate_timeline
from timeline import Timeline


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



def get_parent_profiles(dbstate, uistate, person, router, config=None):
    parents = None
    primary_handle = person.get_main_parents_family_handle()
    if primary_handle:
        parents = Gtk.Expander(expanded=True, use_markup=True)
        parents.set_label("<small><b>{}</b></small>".format(_("Parents and Siblings")))
        elements = Gtk.VBox(spacing=6)
        parents.add(elements)
            
        family = dbstate.db.get_family_from_handle(primary_handle)
        couple = CoupleProfileFrame(dbstate, uistate, family, "parent", "preferences.profile.person", config, router, relation=person)
        children = ChildrenProfileFrame(dbstate, uistate, family, "parent", "preferences.profile.person", config, router, relation=person)
        if children.number > 0:
            expander = Gtk.Expander(expand=True, use_markup=True, expanded=config.get("preferences.profile.person.parent.expand-children"))
            expander.add(children)
            expander.set_label("<b><small>{} {}</small></b>".format(children.number, _("Siblings")))
            couple.pack_start(expander, expand=True, fill=True, padding=0)
        elements.add(couple)

    for handle in person.parent_family_list:
        if handle != primary_handle:
            family = dbstate.db.get_family_from_handle(handle)
            couple = CoupleProfileFrame(dbstate, uistate, family, "parent", "preferences.profile.person", config, router, relation=person)
            children = ChildrenProfileFrame(dbstate, uistate, family, "parent", "preferences.profile.person", config, router, relation=person)
            if children.number > 0:
                expander = Gtk.Expander(expand=True, use_markup=True, expanded=config.get("preferences.profile.person.parent.expand-children"))
                expander.add(children)
                expander.set_label("<b><small>{} {}</small></b>".format(children.number, _("Siblings")))
                couple.pack_start(expander, expand=True, fill=True, padding=0)
            elements.add(couple)
    return parents


def get_spouse_profiles(dbstate, uistate, person, router, config=None):
    spouses = None
    for handle in person.family_list:
        if spouses is None:
            spouses = Gtk.Expander(expanded=True, use_markup=True)
            spouses.set_label("<small><b>{}</b></small>".format(_("Spouses and Children")))
            elements = Gtk.VBox(spacing=6)
            spouses.add(elements)
        family = dbstate.db.get_family_from_handle(handle)
        couple = CoupleProfileFrame(dbstate, uistate, family, "spouse", "preferences.profile.person", config, router, relation=person, parent=person)
        children = ChildrenProfileFrame(dbstate, uistate, family, "spouse", "preferences.profile.person", config, router, relation=person)
        if children.number > 0:
            expander = Gtk.Expander(expand=True, use_markup=True, expanded=config.get("preferences.profile.person.spouse.expand-children"))
            expander.add(children)
            expander.set_label("<b><small>{} {}</small></b>".format(children.number, _("Children")))
            couple.pack_start(expander, expand=True, fill=True, padding=0)        
        elements.pack_start(couple, True, True, 0)
    return spouses


def get_citation_profiles(dbstate, uistate, person, router, config=None):
    citations = None
    for handle in person.citation_list:
        if citations is None:
            citations = Gtk.Expander(expanded=True, use_markup=True)
            citations.set_label("<small><b>{}</b></small>".format(_("Citations")))
            elements = Gtk.VBox(spacing=6)
            citations.add(elements)
        citation = dbstate.db.get_citation_from_handle(handle)
        placard = CitationProfileFrame(dbstate, uistate, citation, "preferences.profile.person", config, router)
        elements.pack_start(placard, True, True, 0)
    return citations


def get_timeline_profiles(dbstate, uistate, person, router, config=None):

    grid, rows = generate_timeline(dbstate, uistate, person, router, config)
    if not rows:
        return None

    timeline = Gtk.Expander(expanded=True, use_markup=True)
    timeline.set_label("<small><b>{}</b></small>".format(_("Timeline")))
    elements = Gtk.VBox(spacing=6)
    timeline.add(elements)
    elements.pack_start(grid, True, True, 0)
    return timeline
