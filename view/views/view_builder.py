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
GrampsObjectView factory and builder functions
"""

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_exceptions import FactoryException
from .view_attribute import AttributeObjectView
from .view_citation import CitationObjectView
from .view_event import EventObjectView
from .view_family import FamilyObjectView
from .view_generic import GenericObjectView
from .view_media import MediaObjectView
from .view_person import PersonObjectView
from .view_source import SourceObjectView
from .view_tag import TagObjectView


def view_factory(grcontext):
    """
    A factory to return an object viewer based on navigation context.
    """
    page_type = grcontext.page_type

    if page_type in [
        "Address",
        "Name",
        "Note",
        "LdsOrd",
        "Place",
        "Repository",
        "ChildRef",
        "EventRef",
        "MediaRef",
        "PersonRef",
        "RepoRef",
    ]:
        cls = GenericObjectView
    elif page_type == "Attribute":
        cls = AttributeObjectView
    elif page_type == "Citation":
        cls = CitationObjectView
    elif page_type == "Event":
        cls = EventObjectView
    elif page_type == "Family":
        cls = FamilyObjectView
    elif page_type == "Media":
        cls = MediaObjectView
    elif page_type == "Person":
        cls = PersonObjectView
    elif page_type == "Source":
        cls = SourceObjectView
    elif page_type == "Tag":
        cls = TagObjectView
    else:
        raise FactoryException(
            "Attempt to create unknown ObjectView class: "
            "classname = %s" % str(page_type)
        )
    return cls


def view_builder(grstate, grcontext):
    """
    A builder to instantiate the view based on navigation context.
    """
    view = view_factory(grcontext)
    return view(grstate, grcontext)
