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
import hashlib
from html import escape


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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.lib import Media, MediaRef, Span
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gui.utils import open_file_with_default_application


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_const import GRAMPS_OBJECTS, _LEFT_BUTTON
from .frame_utils import TextLink, get_config_option, button_activated

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsState class
#
# ------------------------------------------------------------------------
class GrampsState:
    """
    A simple class to encapsulate the state of the Gramps application.
    """

    __slots__ = ("dbstate", "uistate", "router", "config", "page_type")

    def __init__(self, dbstate, uistate, router, config, page_type):
        self.dbstate = dbstate
        self.uistate = uistate
        self.router = router
        self.config = config
        self.page_type = page_type


# ------------------------------------------------------------------------
#
# GrampsOptions class
#
# ------------------------------------------------------------------------
class GrampsOptions:
    """
    A simple class to encapsulate the options for a Gramps frame or list.
    """

    __slots__ = (
        "option_space",
        "size_groups",
        "frame_number",
        "ref_mode",
        "vertical_orientation",
        "family_backlink",
        "relation",
        "parent",
        "context",
    )

    def __init__(self, option_space, size_groups=None, frame_number=0):
        self.option_space = option_space
        self.size_groups = size_groups
        self.frame_number = frame_number
        self.ref_mode = 2
        self.vertical_orientation = True
        self.family_backlink = None
        self.relation = None
        self.parent = None
        self.context = option_space.split(".")[-1]

        if size_groups is None:
            self.size_groups = {
                "age": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "ref": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            }

    def set_ref_mode(self, value):
        """
        Set reference view mode.
        1 = top, 2 = right, 3 = bottom
        """
        self.ref_mode = value

    def set_vertical(self, value):
        """
        Set orientation.
        """
        self.vertical_orientation = value

    def set_backlink(self, value):
        """
        Set family backlink.
        """
        self.family_backlink = value

    def set_number(self, value):
        """
        Set frame number.
        """
        self.frame_number = value

    def set_relation(self, value):
        """
        Set the relation.
        """
        self.relation = value

    def set_parent(self, value):
        """
        Set the relation.
        """
        self.parent = value

    def set_context(self, value):
        """
        Set the context.
        """
        self.context = value


# ------------------------------------------------------------------------
#
# GrampsObject class
#
# ------------------------------------------------------------------------
class GrampsObject:
    """
    A simple class to encapsulate information about a Gramps object.
    """

    __slots__ = (
        "obj",
        "obj_edit",
        "obj_type",
        "obj_lang",
        "dnd_type",
        "dnd_icon",
        "is_reference",
    )

    def __init__(self, obj):
        self.obj = obj
        self.obj_type = None

        for obj_type in GRAMPS_OBJECTS:
            if isinstance(obj, obj_type[0]):
                (
                    dummy_var1,
                    self.obj_edit,
                    self.obj_type,
                    self.obj_lang,
                    self.dnd_type,
                    self.dnd_icon,
                ) = obj_type
                if not self.obj_lang:
                    self.obj_lang = self.obj_type
                break

        if not self.obj_type:
            raise AttributeError
        self.is_reference = "Ref" in self.obj_type

    def __new__(cls, obj):
        if obj:
            return super().__new__(cls)

    @property
    def obj_hash(self):
        """
        Return sha256 hash in digest format.
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(self.obj.serialize()).encode("utf-8"))
        return sha256_hash.hexdigest()


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

    def __init__(self, grstate, groptions):
        self.grstate = grstate
        self.groptions = groptions
        self.markup = "{}"
        if self.grstate.config.get("options.global.use-smaller-detail-font"):
            self.markup = "<small>{}</small>"

    def get_option(self, key, full=True, keyed=False):
        """
        Fetches an option in the frame configuration name space.
        """
        dbid = None
        if keyed:
            dbid = self.grstate.dbstate.db.get_dbid()
        option = "{}.{}".format(self.groptions.option_space, key)
        try:
            return get_config_option(
                self.grstate.config, option, full=full, dbid=dbid
            )
        except AttributeError:
            return False

    def get_layout(self, key):
        """
        Fetches an option in the page layout name space.
        """
        option = "options.page.{}.layout.{}".format(self.grstate.page_type, key)
        try:
            return self.grstate.config.get(option)
        except AttributeError:
            return False

    def make_label(self, data, left=True):
        """
        Simple helper to prepare a label.
        """
        if left:
            label = Gtk.Label(
                hexpand=False,
                halign=Gtk.Align.START,
                justify=Gtk.Justification.LEFT,
                wrap=True,
                xalign=0.0,
            )
        else:
            label = Gtk.Label(
                hexpand=False,
                halign=Gtk.Align.END,
                justify=Gtk.Justification.RIGHT,
                wrap=True,
                xalign=1.0,
            )
        text = data or ""
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
            label=message,
        )
        dialog.vbox.add(label)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        return False


# ------------------------------------------------------------------------
#
# GrampsFrameGrid class
#
# ------------------------------------------------------------------------
class GrampsFrameGrid(Gtk.Grid, GrampsConfig):
    """
    A simple class to manage a fact grid for a Gramps frame.
    """

    __slots__ = (
        "row",
        "cbrouter",
    )

    def __init__(self, grstate, groptions, cbrouter):
        Gtk.Grid.__init__(
            self,
            row_spacing=2,
            column_spacing=6,
            halign=Gtk.Align.START,
            hexpand=False,
        )
        GrampsConfig.__init__(self, grstate, groptions)
        self.cbrouter = cbrouter
        self.row = 0

    def add_fact(self, fact, label=None):
        """
        Add a simple fact.
        """
        if label:
            self.attach(label, 0, self.row, 1, 1)
            self.attach(fact, 1, self.row, 1, 1)
        else:
            self.attach(fact, 0, self.row, 2, 1)
        self.row = self.row + 1

    def add_event(self, event, reference=None, show_age=False):
        """
        Add a formatted event.
        """
        if not event:
            return

        if show_age:
            age = self._fetch_age_text(reference, event)
        else:
            age = None

        event_format = self.get_option("event-format")

        description = ""
        if event_format in [1, 2, 5]:
            column = 1
            name = glocale.translation.sgettext(event.type.xml_str())
            name_label = TextLink(
                name,
                "Event",
                event.get_handle(),
                self.cbrouter,
                bold=False,
                markup=self.markup,
            )
            self.attach(name_label, 0, self.row, 1, 1)
        else:
            column = 0
            description = event.type.get_abbreviation(
                trans_text=glocale.translation.sgettext
            )

        date = glocale.date_displayer.display(event.date)
        place = place_displayer.display_event(self.grstate.dbstate.db, event)

        join = ""
        if date:
            description = "{} {}".format(description, date).strip()
            join = " {}".format(_("in"))

        if event_format in [1, 3] and place:
            description = "{}{} {}".format(description, join, place).strip()

        if age:
            description = "{} {}".format(description, age)

        date_label = TextLink(
            description,
            "Event",
            event.get_handle(),
            self.cbrouter,
            bold=False,
            markup=self.markup,
        )
        if date:
            self.attach(date_label, column, self.row, 1, 1)
            self.row = self.row + 1
        if event_format in [5, 6] and place:
            if event_format in [6]:
                text = "{} {}".format(_("in"), place)
            else:
                text = place
            place_label = TextLink(
                text,
                "Place",
                event.place,
                self.cbrouter,
                bold=False,
                markup=self.markup,
            )
            self.attach(place_label, column, self.row, 1, 1)
            self.row = self.row + 1

    def _fetch_age_text(self, reference, event):
        """
        Return age label if applicable.
        """
        if reference and reference.date and event and event.date:
            span = Span(reference.date, event.date)
            if span.is_valid():
                precision = global_config.get(
                    "preferences.age-display-precision"
                )
                age = str(span.format(precision=precision))
                if age and age != "unknown":
                    return age
        return None


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

    def __init__(self, grstate, obj, obj_ref=None, size=0, crop=True):
        Gtk.Frame.__init__(
            self, expand=False, shadow_type=Gtk.ShadowType.NONE, margin=3
        )
        self.grstate = grstate
        self.obj = obj
        thumbnail = None
        if obj_ref:
            thumbnail = self.get_thumbnail(obj, obj_ref, size, crop)
        elif isinstance(obj, Media):
            thumbnail = self.get_thumbnail(obj, None, size, crop)
        elif obj.get_media_list():
            thumbnail = self.get_thumbnail(
                None, obj.get_media_list()[0], size, crop
            )
        if thumbnail:
            eventbox = Gtk.EventBox()
            eventbox.add(thumbnail)
            self.add(eventbox)
            eventbox.connect("button-press-event", self.view_photo)

    def get_thumbnail(self, media, media_ref, size, crop):
        """
        Get the thumbnail image.
        """
        mobj = media
        if not mobj:
            mobj = self.grstate.dbstate.db.get_media_from_handle(media_ref.ref)
            self.obj = mobj
        if mobj and mobj.get_mime_type()[0:5] == "image":
            rectangle = None
            if media_ref and crop:
                rectangle = media_ref.get_rectangle()
            pixbuf = get_thumbnail_image(
                media_path_full(self.grstate.dbstate.db, mobj.get_path()),
                rectangle=rectangle,
                size=size,
            )
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            return image
        return None

    def view_photo(self, _dummy_obj, event):
        """
        Open the image in the default picture viewer.
        """
        if button_activated(event, _LEFT_BUTTON):
            photo_path = media_path_full(
                self.grstate.dbstate.db, self.obj.get_path()
            )
            open_file_with_default_application(photo_path, self.grstate.uistate)
