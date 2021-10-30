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
Base classes for object and configuration management that others rely on.
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
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .common_const import GRAMPS_OBJECTS
from .common_utils import get_config_option

_ = glocale.translation.sgettext


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

    def __new__(cls, obj):
        if obj:
            return super().__new__(cls)
        return None

    @property
    def is_reference(self):
        """
        Return True if object is a reference.
        """
        reference = "Ref" in self.obj_type
        return reference

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
# GrampsNavigationContext class
#
# ------------------------------------------------------------------------
class GrampsNavigationContext:
    """
    A simple class to encapsulate the Gramps navigation context.
    """

    __slots__ = (
        "primary_obj",
        "reference_obj",
        "secondary_obj",
    )

    def __init__(self, primary_obj, reference_obj, secondary_obj):
        self.primary_obj = primary_obj
        self.reference_obj = reference_obj
        self.secondary_obj = secondary_obj

    @property
    def page_type(self):
        """
        Return page type.
        """
        if self.reference_obj:
            if self.secondary_obj:
                return "{}{}".format(
                    self.reference_obj.obj_type, self.secondary_obj.obj_type
                )
            return self.reference_obj.obj_type
        if self.secondary_obj:
            return self.secondary_obj.obj_type
        return self.primary_obj.obj_type

    @property
    def location(self):
        """
        Return location tuple for navigation history.
        """
        full_tuple = (
            self.page_type,
            self.primary_obj.obj_type,
            self.primary_obj.get_handle(),
            None,
            None,
            None,
            None,
        )
        if self.reference_obj:
            full_tuple[3] = self.reference_obj.obj_type
            full_tuple[4] = self.reference_obj.ref
        if self.secondary_obj:
            full_tuple[5] = self.secondary_obj.obj_type
            full_tuple[6] = self.secondary_obj.obj_hash
        return full_tuple


# ------------------------------------------------------------------------
#
# GrampsState class
#
# ------------------------------------------------------------------------
class GrampsState:
    """
    A simple class to encapsulate the state of the Gramps application.
    """

    __slots__ = ("dbstate", "uistate", "callbacks", "config", "page_type")

    def __init__(self, dbstate, uistate, callbacks, config, page_type):
        self.dbstate = dbstate
        self.uistate = uistate
        self.callbacks = callbacks
        self.config = config
        self.page_type = page_type

    def fetch(self, obj_type, obj_handle):
        """
        Fetches an object from cache if possible.
        """
        return self.callbacks["fetch-object"](obj_type, obj_handle)

    def thumbnail(self, path, rectangle, size):
        """
        Fetches a thumbnail from cache if possible.
        """
        return self.callbacks["fetch-thumbnail"](path, rectangle, size)

    def object_changed(self, obj_type, handle):
        """
        Change page object for simple primary objects.
        """
        return self.callbacks["object-changed"](obj_type, handle)

    def context_changed(self, obj_type, data):
        """
        Change page context across full navigatable spectrum.
        """
        return self.callbacks["context-changed"](obj_type, data)

    def copy_to_clipboard(self, data, handle):
        """
        Copy object to clipboard.
        """
        return self.callbacks["copy-to-clipboard"](data, handle)

    def update_history(self, old, new):
        """
        Update a secondary reference in the navigation history.
        """
        return self.callbacks["update-history-reference"](old, new)


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
        "backlink",
        "relation",
        "parent",
        "context",
        "age_base",
    )

    def __init__(self, option_space, size_groups=None, frame_number=0):
        self.option_space = option_space
        self.size_groups = size_groups
        self.frame_number = frame_number
        self.ref_mode = 1
        self.vertical_orientation = True
        self.backlink = None
        self.relation = None
        self.parent = None
        self.context = option_space.split(".")[-1]
        self.age_base = None

        if size_groups is None:
            self.size_groups = {
                "age": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "attributes": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "ref": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            }

    def set_ref_mode(self, value):
        """
        Set reference view mode.
        0 = top, 1 = right, 2 = bottom
        """
        self.ref_mode = value

    def set_vertical(self, value):
        """
        Set orientation.
        """
        self.vertical_orientation = value

    def set_backlink(self, value):
        """
        Set object backlink reference.
        """
        self.backlink = value

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

    def set_age_base(self, value):
        """
        Set the context.
        """
        self.age_base = value


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
        self.fetch = self.grstate.fetch

    def get_option(self, key, full=True, keyed=False):
        """
        Fetches an option in the frame configuration name space.
        """
        dbid = None
        if keyed:
            dbid = self.grstate.dbstate.db.get_dbid()
        if key[:8] == "options.":
            option = key
        else:
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
        option = "options.page.{}.layout.{}".format(
            self.grstate.page_type, key
        )
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
                hexpand=True,
                vexpand=True,
                halign=Gtk.Align.START,
                valign=Gtk.Align.START,
                justify=Gtk.Justification.LEFT,
                wrap=True,
                xalign=0.0,
            )
        else:
            label = Gtk.Label(
                hexpand=True,
                vexpand=True,
                halign=Gtk.Align.END,
                valign=Gtk.Align.START,
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
