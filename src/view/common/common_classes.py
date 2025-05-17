#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2015-2016  Nick Hall
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
Base classes for object and configuration management that others rely on.
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
import hashlib
import pickle
from abc import abstractmethod
from html import escape

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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.errors import HandleError
from gramps.gen.lib.addressbase import AddressBase
from gramps.gen.lib.attrbase import AttributeRootBase
from gramps.gen.lib.citationbase import CitationBase
from gramps.gen.lib.ldsordbase import LdsOrdBase
from gramps.gen.lib.mediabase import MediaBase
from gramps.gen.lib.notebase import NoteBase
from gramps.gen.lib.primaryobj import BasicPrimaryObject
from gramps.gen.lib.privacybase import PrivacyBase
from gramps.gen.lib.json_utils import object_to_dict
from gramps.gen.lib.tableobj import TableObject
from gramps.gen.lib.tagbase import TagBase
from gramps.gen.lib.urlbase import UrlBase

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .common_const import BUTTON_PRIMARY, GRAMPS_OBJECTS
from .common_utils import (
    TextLink,
    button_pressed,
    find_modified_secondary_object,
    find_reference,
    find_secondary_object,
    get_config_option,
    prepare_markup,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsObject Class
#
# ------------------------------------------------------------------------
class GrampsObject:
    """
    A simple class to encapsulate information about a Gramps object.
    """

    __slots__ = (
        "obj",
        "obj_type",
        "obj_lang",
        "obj_current_hash",
        "dnd_type",
        "dnd_icon",
    )

    def __init__(self, obj):
        self.obj_current_hash = None
        self.load(obj)

    def __new__(cls, obj):
        if obj:
            return super().__new__(cls)
        return None

    def load(self, obj):
        """
        Load object state. Valid for any object type.
        """
        self.obj = obj
        self.obj_type = None
        self.obj_current_hash = None

        for obj_type in GRAMPS_OBJECTS:
            if isinstance(obj, obj_type[0]):
                (
                    dummy_var1,
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

    @property
    def has_handle(self):
        """
        Return True if has handle which is true of all table objects.
        """
        return isinstance(self.obj, TableObject)

    @property
    def has_privacy(self):
        """
        Return True if has privacy.
        """
        return isinstance(self.obj, PrivacyBase)

    @property
    def has_notes(self):
        """
        Return True if has notes.
        """
        return isinstance(self.obj, NoteBase)

    @property
    def has_events(self):
        """
        Return True if has events.
        """
        return hasattr(self.obj, "event_ref_list")

    @property
    def has_citations(self):
        """
        Return True if has citations.
        """
        return isinstance(self.obj, CitationBase)

    @property
    def has_media(self):
        """
        Return True if has media.
        """
        return isinstance(self.obj, MediaBase)

    @property
    def has_attributes(self):
        """
        Return True if has attributes.
        """
        return isinstance(self.obj, AttributeRootBase)

    @property
    def has_urls(self):
        """
        Return True if has urls.
        """
        return isinstance(self.obj, UrlBase)

    @property
    def has_ldsords(self):
        """
        Return True if has lds ordinances.
        """
        return isinstance(self.obj, LdsOrdBase)

    @property
    def has_addresses(self):
        """
        Return True if has addresses.
        """
        return isinstance(self.obj, AddressBase)

    @property
    def has_tags(self):
        """
        Return True if has tags.
        """
        return isinstance(self.obj, TagBase)

    @property
    def is_primary(self):
        """
        Return True if object is a primary object.
        """
        return isinstance(self.obj, BasicPrimaryObject)

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

    def save_hash(self):
        """
        Save current object hash.
        """
        if self.obj_type in [
            "Address",
            "Attribute",
            "EventRef",
            "LdsOrd",
            "Name",
        ]:
            self.obj_current_hash = self.obj_hash

    def sync_hash(self, grstate):
        """
        Update history with new hash value if needed
        """
        if self.obj_type in [
            "Address",
            "Attribute",
            "EventRef",
            "LdsOrd",
            "Name",
        ]:
            current_hash = self.obj_hash
            if current_hash != self.obj_current_hash:
                grstate.update_history(self.obj_current_hash, current_hash)
                self.obj_current_hash = current_hash

    def refresh(self, grstate):
        """
        Refresh object state. Only valid if a primary object.
        """
        assert self.is_primary
        obj = grstate.fetch(self.obj_type, self.obj.handle)
        self.load(obj)

    def commit(self, grstate, reason=None):
        """
        Commit self to the database.
        """
        assert self.is_primary
        if grstate.uistate:
            grstate.uistate.set_busy_cursor(True)
        if reason:
            message = reason
        else:
            message = "%s %s %s" % (
                _("Updated"),
                self.obj_lang,
                self.obj.gramps_id,
            )
        commit_method = grstate.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(message, grstate.dbstate.db) as trans:
            commit_method(self.obj, trans)
        if grstate.uistate:
            grstate.uistate.set_busy_cursor(False)


# ------------------------------------------------------------------------
#
# GrampsContext Class
#
# ------------------------------------------------------------------------
class GrampsContext:
    """
    A simple class to encapsulate the Gramps navigation context.
    """

    __slots__ = (
        "primary_obj",
        "reference_obj",
        "secondary_obj",
        "reference_base_obj",
    )

    def __init__(
        self,
        primary_obj=None,
        reference_obj=None,
        secondary_obj=None,
        reference_base_obj=None,
    ):
        self.primary_obj = None
        self.reference_obj = None
        self.secondary_obj = None
        self.reference_base_obj = None
        self.load(
            primary_obj,
            reference_obj,
            secondary_obj,
            reference_base_obj=reference_base_obj,
        )

    def __getstate__(self):
        """
        Return object state, used for pickling.
        """
        if self.reference_obj:
            reference_obj = self.reference_obj.obj
        else:
            reference_obj = None

        if self.secondary_obj:
            secondary_obj = self.secondary_obj.obj
        else:
            secondary_obj = None

        if self.reference_base_obj:
            reference_base_obj = self.reference_base_obj.obj
        else:
            reference_base_obj = None

        return (
            self.primary_obj.obj,
            reference_obj,
            secondary_obj,
            reference_base_obj,
        )

    def __setstate__(self, state):
        """
        Set object state, used for unpickling.
        """
        (primary_obj, reference_obj, secondary_obj, reference_base_obj) = state
        self.load(
            primary_obj, reference_obj, secondary_obj, reference_base_obj
        )

    @property
    def pickled(self):
        """
        Return pickled self.
        """
        return pickle.dumps(self)

    def load(
        self,
        primary_obj,
        reference_obj,
        secondary_obj,
        reference_base_obj=None,
    ):
        """
        Load objects that provide the context.
        """
        if isinstance(primary_obj, GrampsObject):
            self.primary_obj = primary_obj
        else:
            self.primary_obj = GrampsObject(primary_obj)
        if isinstance(reference_obj, GrampsObject):
            self.reference_obj = reference_obj
        else:
            self.reference_obj = GrampsObject(reference_obj)
        if isinstance(secondary_obj, GrampsObject):
            self.secondary_obj = secondary_obj
        else:
            self.secondary_obj = GrampsObject(secondary_obj)
        if isinstance(reference_base_obj, GrampsObject):
            self.reference_base_obj = reference_base_obj
        else:
            self.reference_base_obj = GrampsObject(reference_base_obj)

    def serialize(self):
        """
        Return serialized data.
        """
        context = {"primary": self.primary_obj.obj}
        if self.secondary_obj:
            context.update({"secondary": self.secondary_obj.obj})
        if self.reference_obj:
            context.update({"reference": self.reference_obj.obj})
        if self.reference_base_obj:
            context.update({"reference_base": self.reference_base_obj.obj})
        return object_to_dict(context)

    @property
    def page_type(self):
        """
        Return page type.
        """
        if self.reference_obj:
            if self.secondary_obj:
                return "%s%s" % (
                    self.reference_obj.obj_type,
                    self.secondary_obj.obj_type,
                )
            return self.reference_obj.obj_type
        if self.secondary_obj:
            return self.secondary_obj.obj_type
        if self.primary_obj:
            return self.primary_obj.obj_type
        return "Dashboard"

    @property
    def page_location(self):
        """
        Return location tuple for navigation history.
        """
        if self.reference_obj:
            reference_obj_type = self.reference_obj.obj_type
            reference_obj_handle = self.reference_obj.obj.ref
        else:
            reference_obj_type = None
            reference_obj_handle = None

        if self.secondary_obj:
            secondary_obj_type = self.secondary_obj.obj_type
            if secondary_obj_type == "Tag":
                secondary_obj_hash = self.secondary_obj.obj.handle
            else:
                secondary_obj_hash = self.secondary_obj.obj_hash
        else:
            secondary_obj_type = None
            secondary_obj_hash = None

        return (
            self.primary_obj.obj_type,
            self.primary_obj.obj.handle,
            reference_obj_type,
            reference_obj_handle,
            secondary_obj_type,
            secondary_obj_hash,
        )

    def load_page_location(self, grstate, history_page_location):
        """
        Load a navigation history location tuple.
        """
        if len(history_page_location) == 6:
            (
                primary_obj_type,
                primary_obj_handle,
                reference_obj_type,
                reference_obj_handle,
                secondary_obj_type,
                secondary_obj_hash,
            ) = history_page_location
        else:
            (
                primary_obj_type,
                primary_obj_handle,
            ) = history_page_location
            reference_obj_type = None
            reference_obj_handle = None
            secondary_obj_type = None
            secondary_obj_hash = None

        primary_obj = grstate.fetch(primary_obj_type, primary_obj_handle)
        if reference_obj_type and reference_obj_handle:
            reference_obj = find_reference(
                primary_obj, reference_obj_type, reference_obj_handle
            )
        else:
            reference_obj = None

        if secondary_obj_type and secondary_obj_hash:
            if reference_obj:
                secondary_obj = find_secondary_object(
                    reference_obj,
                    secondary_obj_type,
                    secondary_obj_hash,
                )
            else:
                secondary_obj = find_secondary_object(
                    primary_obj,
                    secondary_obj_type,
                    secondary_obj_hash,
                )
        else:
            secondary_obj = None
        self.load(primary_obj, reference_obj, secondary_obj)

    @property
    def obj_key(self):
        """
        Return a unique object key
        """
        if self.primary_obj:
            key = self.primary_obj.obj.handle
        else:
            key = "dashboard"
        if self.reference_obj:
            key = "%s-%s" % (key, self.reference_obj.obj.ref)
        if self.secondary_obj:
            key = "%s-%s" % (key, self.secondary_obj.obj_hash)
        return key

    def refresh(self, grstate):
        """
        Refresh current context state as something changed.
        """
        new_primary_obj = grstate.fetch("Person", self.primary_obj.obj.handle)
        old_primary_obj = self.primary_obj.obj
        self.primary_obj = GrampsObject(new_primary_obj)

        if self.reference_obj:
            new_reference_obj = find_reference(
                new_primary_obj,
                self.reference_obj.obj_type,
                self.reference_obj.obj.ref,
            )
            self.reference_obj = GrampsObject(new_reference_obj)

        if self.secondary_obj:
            new_secondary_obj = find_modified_secondary_object(
                self.secondary_obj.obj_type, old_primary_obj, new_primary_obj
            )
            self.secondary_obj = GrampsObject(new_secondary_obj)


# ------------------------------------------------------------------------
#
# GrampsState Class
#
# ------------------------------------------------------------------------
class GrampsState:
    """
    A simple class to encapsulate the state of the Gramps application.
    """

    __slots__ = (
        "dbstate",
        "uistate",
        "callbacks",
        "config",
        "page_type",
        "methods",
        "templates",
    )

    def __init__(self, dbstate, uistate, callbacks, config):
        self.dbstate = dbstate
        self.uistate = uistate
        self.callbacks = callbacks
        self.config = config
        self.page_type = ""
        if callbacks:
            self.methods = callbacks.get("methods")
        self.templates = None

    def set_templates(self, templates):
        """
        Set the templates configuration manager.
        """
        self.templates = templates

    def set_config(self, config):
        """
        Set the configation manager.
        """
        self.config = config

    def set_page_type(self, page_type):
        """
        Set the page type.
        """
        self.page_type = page_type

    def fetch(self, obj_type, obj_handle):
        """
        Fetches an object from the database.
        """
        try:
            return self.methods[obj_type](obj_handle)
        except HandleError:
            return None

    def fetch_page_context(self):
        """
        Fetches active page context.
        """
        return self.callbacks["fetch-page-context"]()

    def load_page(self, context):
        """
        Load the proper page for the given context.
        """
        return self.callbacks["load-page"](context)

    def load_primary_page(self, obj_type, obj_or_handle):
        """
        Load page for a primary object.
        """
        if isinstance(obj_or_handle, str):
            obj = self.fetch(obj_type, obj_or_handle)
        else:
            obj = obj_or_handle
        context = GrampsContext(obj, None, None)
        return self.load_page(context.pickled)

    def reload_config(self, refresh_only=False, defer_refresh=True):
        """
        Reload the configuration and page.
        """
        return self.callbacks["reload-config"](
            refresh_only=refresh_only, defer_refresh=defer_refresh
        )

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

    def update_history_object(self, old_hash, obj):
        """
        Update old secondary reference for object in the navigation history.
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(obj.serialize()).encode("utf-8"))
        return self.callbacks["update-history-reference"](
            old_hash, sha256_hash.hexdigest()
        )

    def show_group(self, obj, group_type, title=None):
        """
        Display a group of objects.
        """
        return self.callbacks["show-group"](obj, group_type, title)

    def launch_config(self, label, builder, space, context):
        """
        Launch a configuration dialog page.
        """
        return self.callbacks["launch-config"](label, builder, space, context)

    def set_dirty_redraw_trigger(self):
        """
        Set trigger to mark current page dirty if needed.
        """
        return self.callbacks["set-dirty-redraw-trigger"]()


# ------------------------------------------------------------------------
#
# GrampsOptions Class
#
# ------------------------------------------------------------------------
class GrampsOptions:
    """
    A simple class to encapsulate the options for a Gramps card or list.
    """

    def __init__(self, option_space, size_groups=None, card_number=0):
        self.option_space = option_space
        self.context = option_space.split(".")[-1]
        self.card_number = card_number
        self.size_groups = size_groups
        self.ref_mode = 0
        self.vertical_orientation = True
        self.backlink = None
        self.relation = None

        self.age_base = None

        if size_groups is None:
            self.size_groups = {
                "ref": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "age": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "attributes": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            }

    def __getattr__(self, key):
        """
        If there is no key set return None.
        """
        return None

    def set_ref_mode(self, value):
        """
        Set reference view mode.
        0 = none, 1 = left, 2 = top, 3 = right, 4 = bottom
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
        Set card number.
        """
        self.card_number = value

    def set_relation(self, value):
        """
        Set the relation.
        """
        self.relation = value

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
# GrampsConfig Class
#
# ------------------------------------------------------------------------
class GrampsConfig:
    """
    The GrampsConfig class provides the basis for handling configuration
    related information and helper methods common to both the GrampsCard
    and the various GrampsCardGroup classes.
    """

    def __init__(self, grstate, groptions):
        self.grstate = grstate
        self.groptions = groptions

        scheme = global_config.get("colors.scheme")
        self.detail_markup = prepare_markup(grstate.config, scheme=scheme)
        self.title_markup = prepare_markup(
            grstate.config, key="title", scheme=scheme
        )
        self.fetch = self.grstate.fetch

    def get_option(self, key, full=True):
        """
        Fetches an option in the card configuration name space.
        """
        if key[:5] in ["activ", "group"]:
            option = key
        else:
            option = "%s.%s" % (self.groptions.option_space, key)
        try:
            return get_config_option(self.grstate.config, option, full=full)
        except AttributeError:
            return False

    def get_label(self, data, left=True, italic=False):
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
        if text:
            text = escape(text)
        if italic:
            text = "<i>%s</i>" % text
        label.set_markup(self.detail_markup.format(text))
        return label

    def get_link(
        self,
        description,
        obj_type,
        obj_handle,
        callback=None,
        title=True,
        hexpand=False,
        tooltip=None,
    ):
        """
        Simple helper to prepare a link.
        """
        callback = callback or self.grstate.load_primary_page
        if title:
            markup = self.title_markup
        else:
            markup = self.detail_markup
        return TextLink(
            description,
            obj_type,
            obj_handle,
            callback,
            bold=title,
            markup=markup,
            hexpand=hexpand,
            tooltip=tooltip,
        )


# ------------------------------------------------------------------------
#
# GrampsBaseIcon Class
#
# ------------------------------------------------------------------------
class GrampsBaseIcon(Gtk.EventBox):
    """
    A simple class for a manged icon.
    """

    def __init__(
        self, grstate, name, size=Gtk.IconSize.SMALL_TOOLBAR, tooltip=None
    ):
        Gtk.EventBox.__init__(self)
        self.grstate = grstate
        icon = Gtk.Image()
        icon.set_from_icon_name(name, size)
        self.add(icon)
        if tooltip:
            self.set_tooltip_text(tooltip)

        self.connect("button-press-event", self.__icon_press)
        self.connect("button-release-event", self.__icon_release)

    def __icon_press(self, _dummy_obj, event):
        """
        Handle icon click.
        """
        if not button_pressed(event, BUTTON_PRIMARY):
            return False
        self.icon_clicked(event)
        return True

    def __icon_release(self, *_dummy_args):
        """
        Sink action.
        """
        return True

    @abstractmethod
    def icon_clicked(self, event):
        """
        To be set in derived classes.
        """
