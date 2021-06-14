# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2015-2016  Nick Hall
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
ImageFrame for Profile Views
"""

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk


#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gen.utils.file import media_path_full
from gramps.gui.utils import open_file_with_default_application


class ImageFrame(Gtk.Frame):
    """
    Simple class for managing display of an image.
    """

    def __init__(self, db, uistate, obj, size=0):
        Gtk.Frame.__init__(self, expand=False, shadow_type=Gtk.ShadowType.NONE)
        self.db = db
        self.uistate = uistate
        media = obj.get_media_list()
        if media:
            thumbnail = self.get_thumbnail(media[0], size)
            if thumbnail:
                self.add(thumbnail)

    def get_thumbnail(self, media_ref, size):
        mobj = self.db.get_media_from_handle(media_ref.ref)
        if mobj and mobj.get_mime_type()[0:5] == "image":
            pixbuf = get_thumbnail_image(
                media_path_full(self.db, mobj.get_path()),
                rectangle=media_ref.get_rectangle(),
                size=size)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            button = Gtk.Button(relief=Gtk.ReliefStyle.NONE)
            button.add(image)
            button.connect("clicked", lambda obj: self.view_photo(mobj))
            button.show_all()
            return button
        return None

    def view_photo(self, photo):
        """
        Open this picture in the default picture viewer.
        """
        photo_path = media_path_full(self.db, photo.get_path())
        open_file_with_default_application(photo_path, self.uistate)
