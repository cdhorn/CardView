#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
BookmarkAction
"""

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .action_base import GrampsAction
from ..common.common_utils import get_bookmarks


# ------------------------------------------------------------------------
#
# BookmarkAction class
#
# action_object is the TableObject, a primary Gramps object other than Tag
#
# ------------------------------------------------------------------------
class BookmarkAction(GrampsAction):
    """
    Class to support toggling the bookmark state for an object.
    """

    def __init__(self, grstate, action_object, callback=None):
        GrampsAction.__init__(self, grstate, action_object)
        self.callback = callback

    def set_callback(self, callback):
        """
        Set the callback.
        """
        self.callback = callback

    def is_set(self, *_dummy_args):
        """
        Return true if bookmark set.
        """
        bookmarks = get_bookmarks(self.db, self.action_object.obj_type).get()
        if self.action_object.obj.get_handle() in bookmarks:
            return True
        return False

    def toggle(self, *_dummy_args):
        """
        Toggle the bookmark state.
        """
        bookmarks = get_bookmarks(self.db, self.action_object.obj_type)
        if self.is_set():
            bookmarks.remove(self.action_object.obj.get_handle())
        else:
            bookmarks.insert(0, self.action_object.obj.get_handle())
        if self.callback:
            self.callback(self.action_object)
