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
GrampsFrame base classes
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from html import escape


# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk, Gdk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Media
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gui.utils import open_file_with_default_application


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_utils import get_config_option

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_SPACE = Gdk.keyval_from_name("space")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3


def button_activated(event, mouse_button):
    """
    Test if specific button press happened.
    """
    return (
        event.type == Gdk.EventType.BUTTON_PRESS and event.button == mouse_button
    ) or (
        event.type == Gdk.EventType.KEY_PRESS
        and event.keyval in (_RETURN, _KP_ENTER, _SPACE)
    )


# ------------------------------------------------------------------------
#
# GrampsState class
#
# ------------------------------------------------------------------------
class GrampsState:
    """
    A simple class to encapsulate the underlying state for the page view.
    """

    __slots__ = 'dbstate', 'uistate', 'router', 'space', 'config'

    def __init__(self, dbstate, uistate, router, space, config):
        self.dbstate = dbstate
        self.uistate = uistate
        self.router = router
        self.space = space
        self.config = config


# ------------------------------------------------------------------------
#
# GrampsConfig class
#
# ------------------------------------------------------------------------
class GrampsConfig:
    """
    The GrampsConfig class provides the basis for handling configuration
    related information and helper methods common to both the GrampsFrame
    and the various GrampsFrameGroup classes.
    """

    def __init__(self, grstate):
        self.grstate = grstate
        self.context = ""
        self.markup = "{}"
        if self.grstate.config.get("options.global.use-smaller-detail-font"):
            self.markup = "<small>{}</small>"

    def option(self, context, name, full=True, keyed=False):
        """
        Fetches an option from the given context in a configuration name space.
        """
        dbid = None
        if keyed:
            dbid = self.grstate.dbstate.db.get_dbid()
        option = "{}.{}.{}".format(self.grstate.space, context, name)
        try:
            return get_config_option(self.grstate.config, option, full=full, dbid=dbid)
        except AttributeError:
            return False

    def make_label(self, text, left=True):
        """
        Simple helper to prepare a label.
        """
        if left:
            label = Gtk.Label(
                hexpand=False,
                halign=Gtk.Align.START,
                wrap=True,
            )
        else:
            label = Gtk.Label(
                hexpand=False,
                halign=Gtk.Align.END,
                wrap=True,
            )
        label.set_markup(self.markup.format(escape(text)))
        return label

    def confirm_action(self, title, message):
        """
        If enabled display message and confirm a user requested action.
        """
        if not self.grstate.config.get("options.global.enable-warnings"):
            return True
        dialog = Gtk.Dialog(parent=self.grstate.uistate.window)
        dialog.set_title(title)
        dialog.set_default_size(500, 300)
        dialog.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("_OK", Gtk.ResponseType.OK)

        label = Gtk.Label(
            hexpand=True,
            vexpand=True,
            halign=Gtk.Align.CENTER,
            justify=Gtk.Justification.CENTER,
            use_markup=True,
            wrap=True,
            label=message
        )
        dialog.vbox.add(label)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        return False

    def switch_object(self, obj, event, obj_type, handle):
        """
        Change active object for the view.
        """
        self.grstate.router('object-changed', (obj_type, handle))


# ------------------------------------------------------------------------
#
# GrampsImageViewFrame class
#
# ------------------------------------------------------------------------
class GrampsImageViewFrame(Gtk.Frame):
    """
    A simple class for managing display of an image intended for embedding
    in a GrampsFrame object.
    """

    def __init__(self, grstate, obj, size=0):
        Gtk.Frame.__init__(self, expand=False, shadow_type=Gtk.ShadowType.NONE)
        self.grstate = grstate
        if isinstance(obj, Media):
            thumbnail = self.get_thumbnail(obj, None, size)
            self.add(thumbnail)
            return
        if obj.get_media_list():
            thumbnail = self.get_thumbnail(None, obj.get_media_list()[0], size)
            if thumbnail:
                self.add(thumbnail)

    def get_thumbnail(self, media, media_ref, size):
        """
        Get the thumbnail image.
        """
        mobj = media
        if not mobj:
            mobj = self.grstate.dbstate.db.get_media_from_handle(media_ref.ref)
        if mobj and mobj.get_mime_type()[0:5] == "image":
            rectangle=None
            if media_ref:
                media_ref.get_rectangle()
            pixbuf = get_thumbnail_image(
                media_path_full(self.grstate.dbstate.db, mobj.get_path()),
                rectangle=rectangle,
                size=size,
            )
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
        Open the image in the default picture viewer.
        """
        photo_path = media_path_full(self.grstate.dbstate.db, photo.get_path())
        open_file_with_default_application(photo_path, self.grstate.uistate)
