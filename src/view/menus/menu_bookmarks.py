#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022       Christopher Horn
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
Bookmarks menu
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
from functools import partial

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
from gramps.gui.views.bookmarks import (
    PersonBookmarks,
    FamilyBookmarks,
    EventBookmarks,
    PlaceBookmarks,
    CitationBookmarks,
    SourceBookmarks,
    RepoBookmarks,
    MediaBookmarks,
    NoteBookmarks,
)

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .menu_utils import (
    menu_item,
    new_menu,
    show_menu,
    add_double_separator,
    submenu_item,
)

_ = glocale.translation.sgettext

BOOKMARK_TYPES = [
    ("Person", _("People"), PersonBookmarks, "gramps-person"),
    ("Family", _("Families"), FamilyBookmarks, "gramps-family"),
    ("Event", _("Events"), EventBookmarks, "gramps-event"),
    ("Place", _("Places"), PlaceBookmarks, "gramps-place"),
    ("Media", _("Media"), MediaBookmarks, "gramps-media"),
    ("Note", _("Notes"), NoteBookmarks, "gramps-note"),
    ("Citations", _("Citations"), CitationBookmarks, "gramps-citation"),
    ("Source", _("Source"), SourceBookmarks, "gramps-source"),
    ("Repository", _("Repository"), RepoBookmarks, "gramps-repository"),
]


def build_bookmark_menu(grstate, parent_menu, bookmark_type):
    """
    Build bookmark submenu for specific bookmark type.
    """
    (obj_type, obj_type_lang, bookmark_class, icon) = bookmark_type
    bookmark_handler = bookmark_class(grstate.dbstate, grstate.uistate, None)
    bookmark_handles = bookmark_handler.get_bookmarks().get()
    if bookmark_handles:
        menu = new_menu(
            "list-add",
            _("Organize Bookmarks"),
            edit_bookmarks,
            bookmark_handler,
        )
        add_double_separator(menu)
        for obj_handle in bookmark_handles:
            title, dummy_obj = bookmark_handler.make_label(obj_handle)
            goto_object = partial(goto_bookmark, grstate, obj_type, obj_handle)
            menu.add(menu_item("go-next", title, goto_object))
        parent_menu.append(submenu_item(icon, obj_type_lang, menu))


def edit_bookmarks(_dummy_arg, bookmarks):
    """
    Organize bookmarks.
    """
    bookmarks.edit()
    return True


def goto_bookmark(grstate, obj_type, obj_handle, *_dummy_args):
    """
    Go to desired bookmark.
    """
    grstate.load_primary_page(obj_type, obj_handle)
    return True


def build_bookmarks_menu(widget, grstate, event):
    """
    Build the bookmarks menu.
    """
    menu = Gtk.Menu()
    for bookmark_type in BOOKMARK_TYPES:
        build_bookmark_menu(grstate, menu, bookmark_type)
    return show_menu(menu, widget, event)
