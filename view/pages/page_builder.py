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
GrampsPageView factory and builder functions
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_exceptions import FactoryException
from .page_base import GrampsPageView
from .page_event import EventPageView
from .page_family import FamilyPageView
from .page_person import PersonPageView


def page_factory(page_type):
    """
    A factory to return an object page.
    """
    if page_type in [
        "Address",
        "Attribute",
        "ChildRef",
        "Citation",
        "Media",
        "MediaRef",
        "Name",
        "Note",
        "LdsOrd",
        "Place",
        "Repository",
        "RepoRef",
        "Source",
        "Tag",
    ]:
        cls = GrampsPageView
    elif page_type in [
        "Person",
        "PersonRef",
    ]:
        cls = PersonPageView
    elif page_type in [
        "Event",
        "EventRef",
    ]:
        cls = EventPageView
    elif page_type == "Family":
        cls = FamilyPageView
    else:
        raise FactoryException(
            "Attempt to create unknown GrampsPageView class: "
            "classname = %s" % str(page_type)
        )
    return cls


def page_builder(parent_view, page_type, grstate):
    """
    A builder to instantiate a particular page type.
    """
    page = page_factory(page_type)
    return page(parent_view, page_type, grstate)
