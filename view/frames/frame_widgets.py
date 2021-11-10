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
Widgets supporting various sections of the frame.
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
import pickle
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
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.lib import Media, MediaRef
from gramps.gen.lib.date import Today
from gramps.gen.utils.file import media_path_full
from gramps.gui.utils import open_file_with_default_application

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsConfig, GrampsContext
from ..common.common_const import _LEFT_BUTTON
from ..common.common_utils import (
    TextLink,
    button_activated,
    get_age,
    get_bookmarks,
    pack_icon,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsFrameId class
#
# ------------------------------------------------------------------------
class GrampsFrameId(Gtk.HBox, GrampsConfig):
    """
    A class to display the id and privacy for a GrampsFrame object.
    """

    def __init__(self, grstate, groptions):
        Gtk.HBox.__init__(
            self,
            hexpand=True,
            vexpand=False,
            halign=Gtk.Align.END,
            valign=Gtk.Align.START,
        )
        GrampsConfig.__init__(self, grstate, groptions)

    def load(self, obj, obj_type, gramps_id=None):
        """
        Load the id field as needed for the given object.
        """
        if hasattr(obj, "gramps_id"):
            self.add_gramps_id(obj=obj)
        elif gramps_id:
            self.add_gramps_id(gramps_id=gramps_id)
        if hasattr(obj, "handle"):
            self.add_bookmark_indicator(obj, obj_type)
        elif "Ref" in obj_type:
            pack_icon(self, "stock_link")
        self.add_privacy_indicator(obj)
        self.show_all()

    def reload(self, obj, obj_type, gramps_id=None):
        """
        Reload the field.
        """
        list(map(self.remove, self.get_children()))
        self.load(obj, obj_type, gramps_id=gramps_id)

    def add_gramps_id(self, obj=None, gramps_id=""):
        """
        Add the gramps id if needed.
        """
        if self.grstate.config.get("options.global.enable-gramps-ids"):
            if obj:
                text = obj.gramps_id
            else:
                text = gramps_id
            label = Gtk.Label(
                use_markup=True,
                label=self.markup.format(escape(text)),
            )
            self.pack_end(label, False, False, 0)

    def add_bookmark_indicator(self, obj, obj_type):
        """
        Add the bookmark indicator if needed.
        """
        if self.grstate.config.get("options.global.enable-bookmarks"):
            for bookmark in get_bookmarks(
                self.grstate.dbstate.db, obj_type
            ).get():
                if bookmark == obj.get_handle():
                    pack_icon(self, "gramps-bookmark")
                    break

    def add_privacy_indicator(self, obj):
        """
        Add privacy mode indicator if needed.
        """
        mode = self.grstate.config.get("options.global.privacy-mode")
        if mode:
            image = Gtk.Image()
            if obj.private:
                if mode in [1, 3]:
                    image.set_from_icon_name(
                        "gramps-lock", Gtk.IconSize.BUTTON
                    )
            else:
                if mode in [2, 3]:
                    image.set_from_icon_name(
                        "gramps-unlock", Gtk.IconSize.BUTTON
                    )
            self.pack_end(image, False, False, 0)


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

    def __init__(self, grstate, groptions, cbrouter, right=False):
        Gtk.Grid.__init__(
            self,
            row_spacing=2,
            column_spacing=6,
            halign=Gtk.Align.START,
            valign=Gtk.Align.START,
            hexpand=True,
        )
        GrampsConfig.__init__(self, grstate, groptions)
        self.cbrouter = cbrouter
        self.row = 0
        if right:
            self.set_halign(Gtk.Align.END)

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

        event_format = self.get_option("event-format")

        description = ""
        if event_format in [1, 2, 5]:
            column = 1
            label = TextLink(
                glocale.translation.sgettext(event.type.xml_str()),
                "Event",
                event.get_handle(),
                self.cbrouter,
                bold=False,
                markup=self.markup,
            )
            self.attach(label, 0, self.row, 1, 1)
        else:
            column = 0
            description = event.type.get_abbreviation(
                trans_text=glocale.translation.sgettext
            )

        join = ""
        date = glocale.date_displayer.display(event.date)
        if date:
            description = "{} {}".format(description, date).strip()
            join = " {}".format(_("in"))

        place = place_displayer.display_event(self.grstate.dbstate.db, event)
        if event_format in [1, 3] and place:
            description = "{}{} {}".format(description, join, place).strip()

        if show_age:
            description = "{} {}".format(
                description, get_age(reference, event)
            ).strip()

        if date:
            label = TextLink(
                description,
                "Event",
                event.get_handle(),
                self.cbrouter,
                bold=False,
                markup=self.markup,
            )
            self.attach(label, column, self.row, 1, 1)
            self.row = self.row + 1

        if event_format in [5, 6] and place:
            if event_format in [6]:
                text = "{} {}".format(_("in"), place)
            else:
                text = place
            label = TextLink(
                text,
                "Place",
                event.place,
                self.cbrouter,
                bold=False,
                markup=self.markup,
            )
            self.attach(label, column, self.row, 1, 1)
        self.row = self.row + 1

    def add_living(self, birth, show_age=False):
        """
        Add death event setting text to indicate living.
        """
        age = ""
        if birth and show_age:
            today = Today()
            age = get_age(birth, None, today=today)

        event_format = self.get_option("event-format")
        if event_format in [1, 2, 5]:
            label = self.make_label(_("Living"))
            value = self.make_label("{}".format(age.strip("()")))
            self.add_fact(value, label=label)
        elif event_format in [3, 4, 6]:
            value = self.make_label("{}. {}".format(_("liv"), age.strip("()")))
            self.add_fact(value)


# ------------------------------------------------------------------------
#
# GrampsFrameIcons class
#
# ------------------------------------------------------------------------
class GrampsFrameIcons(Gtk.HBox, GrampsConfig):
    """
    A simple class for managing display of the child indicator and tag
    icons for a Gramps object.
    """

    def __init__(self, grstate, groptions, right_justify=False):
        if right_justify:
            justify = Gtk.Align.END
        else:
            justify = Gtk.Align.START            
        Gtk.HBox.__init__(self, halign=justify, valign=Gtk.Align.END)
        GrampsConfig.__init__(self, grstate, groptions)
        self.flowbox = Gtk.FlowBox(
            orientation=Gtk.Orientation.HORIZONTAL,
            homogeneous=False,
            valign=Gtk.Align.END,
            halign=justify
        )
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        if "active" in self.groptions.option_space:
            size = self.grstate.config.get("options.global.icons-active-width")
        else:
            size = self.grstate.config.get("options.global.icons-group-width")
        self.flowbox.set_min_children_per_line(size)
        self.flowbox.set_max_children_per_line(size)
        self.pack_end(self.flowbox, True, True, 0)
        self.obj = None
        self.obj_type = None

    def load(self, obj, obj_type):
        """
        Load icons for an object.
        """
        self.obj = obj
        self.obj_type = obj_type

        if self.grstate.config.get("options.global.icons-enable-indicators"):
            self.load_indicators()

        if self.grstate.config.get("options.global.icons-enable-tags"):
            if hasattr(obj, "tag_list"):
                self.load_tags()
        self.show_all()

    def load_indicators(self):
        """
        Load child icon indicators for an object.
        """
        obj = self.obj
        obj_type = self.obj_type
        check = self.grstate.config.get

        if obj_type == "Person":
            self.__load_person(obj, check)
        elif (
            obj_type == "Family"
            and check("options.global.indicate-children")
            and obj.get_child_ref_list()
        ):
            self.__add_icon("gramps-person", "child", tooltip=_("Children"))
        if (
            check("options.global.indicate-events")
            and hasattr(obj, "event_ref_list")
            and obj.get_event_ref_list()
        ):
            self.__add_icon("gramps-event", "event", tooltip=_("Events"))
        if (
            check("options.global.indicate-ordinances")
            and hasattr(obj, "lds_ord_list")
            and obj.get_lds_ord_list()
        ):
            self.__add_icon(
                "emblem-documents", "ordinance", tooltip=_("Ordinances")
            )
        if (
            check("options.global.indicate-attributes")
            and hasattr(obj, "attribute_list")
            and obj.get_attribute_list()
        ):
            self.__add_icon(
                "gramps-attribute", "attribute", tooltip=_("Attributes")
            )
        if (
            check("options.global.indicate-media")
            and hasattr(obj, "media_list")
            and obj.get_media_list()
        ):
            self.__add_icon("gramps-media", "media", tooltip=_("Media"))
        if (
            check("options.global.indicate-citations")
            and hasattr(obj, "citation_list")
            and obj.get_citation_list()
        ):
            self.__add_icon(
                "gramps-citation", "citation", tooltip=_("Citations")
            )
        if (
            check("options.global.indicate-notes")
            and hasattr(obj, "note_list")
            and obj.get_note_list()
        ):
            self.__add_icon("gramps-notes", "note", tooltip=_("Notes"))
        if (
            check("options.global.indicate-addresses")
            and hasattr(obj, "address_list")
            and obj.get_address_list()
        ):
            self.__add_icon(
                "gramps-address", "address", tooltip=_("Addresses")
            )
        if (
            check("options.global.indicate-urls")
            and hasattr(obj, "urls")
            and obj.get_url_list()
        ):
            self.__add_icon("gramps-url", "url", tooltip=_("Urls"))

    def __load_person(self, obj, check):
        """
        Examine and load indicators for a person.
        """
        if (
            check("options.global.indicate-names")
            and obj.get_alternate_names()
        ):
            self.__add_icon("user-info", "name", tooltip=_("Names"))
        if (
            check("options.global.indicate-parents")
            and obj.get_parent_family_handle_list()
        ):
            self.__add_icon("gramps-family", "parent", tooltip=_("Parents"))
        if (
            check("options.global.indicate-spouses")
            and obj.get_family_handle_list()
        ):
            self.__add_icon("gramps-spouse", "spouse", tooltip=_("Spouses"))
        if (
            check("options.global.indicate-associations")
            and obj.get_person_ref_list()
        ):
            self.__add_icon(
                "gramps-person", "association", tooltip=_("Associations")
            )

    def __add_icon(self, icon_name, group_type, tooltip=None):
        """
        Add an indicator icon.
        """
        icon = Gtk.Image(halign=Gtk.Align.END)
        icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        eventbox = Gtk.EventBox(tooltip_text=tooltip)
        eventbox.add(icon)
        eventbox.connect(
            "button-press-event", self.__indicator_click, group_type
        )
        self.flowbox.add(eventbox)

    def __indicator_click(self, _dummy_obj, _dummy_event, group_type):
        """
        Launch group dialog.
        """
        self.grstate.show_group(self.obj, group_type)

    def load_tags(self):
        """
        Load tags for an object.
        """
        tags = []
        for handle in self.obj.get_tag_list():
            tag = self.fetch("Tag", handle)
            tags.append(tag)

        if self.grstate.config.get("options.global.sort-tags-by-name"):
            tags.sort(key=lambda x: x.name)
        else:
            tags.sort(key=lambda x: x.priority)

        for tag in tags:
            icon = Gtk.Image()
            icon.set_from_icon_name("gramps-tag", Gtk.IconSize.BUTTON)
            css = (
                ".image {{ "
                "margin: 0px; "
                "padding: 0px; "
                "background-image: none; "
                "background-color: {}; }}".format(
                    tag.color[:7],
                )
            )
            css = css.encode("utf-8")
            provider = Gtk.CssProvider()
            provider.load_from_data(css)
            context = icon.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            context.add_class("image")
            eventbox = Gtk.EventBox(tooltip_text=tag.name)
            eventbox.add(icon)
            eventbox.connect(
                "button-press-event", self.__tag_click, tag.handle
            )
            self.flowbox.add(eventbox)

    def __tag_click(self, _dummy_obj, _dummy_event, handle):
        """
        Request page for tag.
        """
        tag = self.fetch("Tag", handle)
        page_context = GrampsContext(tag, None, None)
        return self.grstate.load_page(page_context.pickled)


# ------------------------------------------------------------------------
#
# GrampsImage class
#
# ------------------------------------------------------------------------
class GrampsImage(Gtk.EventBox):
    """
    A simple class for managing display of an image for a GrampsFrame object.
    """

    def __init__(self, grstate, obj=None, media_ref=None, active=False):
        Gtk.EventBox.__init__(self)
        self.grstate = grstate
        self.media_ref = None
        self.active = active

        if isinstance(obj, Media):
            self.media = obj
        elif isinstance(media_ref, MediaRef):
            self.media_ref = media_ref
            self.media = grstate.fetch("Media", media_ref.ref)
        elif hasattr(obj, "media_list") and obj.get_media_list():
            self.media = grstate.fetch("Media", obj.get_media_list()[0].ref)
        else:
            self.media = None

        if self.media:
            self.path = media_path_full(
                self.grstate.dbstate.db, self.media.get_path()
            )

    def load(self, size=0, crop=True):
        """
        Load or reload an image.
        """
        if self.media:
            list(map(self.remove, self.get_children()))
            thumbnail = self.__get_thumbnail(size, crop)
            if thumbnail:
                self.add(thumbnail)
                self.connect("button-press-event", self.handle_click)

    def __get_thumbnail(self, size, crop):
        """
        Get the thumbnail image.
        """
        if self.media and self.media.get_mime_type()[0:5] == "image":
            rectangle = None
            if self.media_ref and crop:
                rectangle = self.media_ref.get_rectangle()
            pixbuf = self.grstate.thumbnail(self.path, rectangle, size)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            return image
        return None

    def handle_click(self, _dummy_obj, event):
        """
        Open the image in the default picture viewer.
        """
        if button_activated(event, _LEFT_BUTTON):
            if not self.active:
                if self.grstate.config.get("options.global.image-page-link"):
                    context = GrampsContext(self.media, None, None)
                    return self.grstate.load_page(context.pickled)
            return open_file_with_default_application(
                self.path, self.grstate.uistate
            )
