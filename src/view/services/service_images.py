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
ImagesService
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
from functools import lru_cache

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.utils.thumbnails import get_thumbnail_image


# -------------------------------------------------------------------------
#
# ImagesService
#
# -------------------------------------------------------------------------
class ImagesService:
    """
    A singleton class that wraps image lookups with a LRU cache.
    """

    def __new__(cls):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(ImagesService, cls).__new__(cls)
        return cls.instance

    @lru_cache(maxsize=64)
    def get_thumbnail_image(self, path, rectangle, size):
        """
        Fetch a thumbnail.
        """
        return get_thumbnail_image(path, rectangle=rectangle, size=size)

    def get_cache_info(self):
        """
        Return cache info.
        """
        return self.get_thumbnail_image.cache_info()
