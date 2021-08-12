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
PrimaryGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from html import escape
import pickle
import time


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
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gui.editors import (
    EditAttribute,
    EditChildRef,
    EditEventRef,
    EditPerson,
    EditSrcAttribute,
    EditUrl,
)
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    Attribute,
    ChildRef,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    Name,
    Person,
    SrcAttribute,
    Span,
    Surname,
    Tag,
    Url,
)
from gramps.gen.utils.db import preset_name
from gramps.gui.display import display_url
from gramps.gui.selectors import SelectorFactory
from gramps.gui.views.tags import OrganizeTagsDialog, EditTag


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_base import GrampsFrame
from .frame_classes import GrampsImageViewFrame
from .frame_selectors import get_attribute_types
from .frame_utils import (
    attribute_option_text,
    get_bookmarks,
    menu_item,
    submenu_item,
    TextLink,
)

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# PrimaryGrampsFrame class
#
# ------------------------------------------------------------------------
class PrimaryGrampsFrame(GrampsFrame):
    """
    The PrimaryGrampsFrame class provides core methods for constructing the
    view and working with the primary Gramps object it exposes.
    """

    def __init__(
        self,
        grstate,
        groptions,
        primary_obj,
        secondary_obj=None,
    ):
        Gtk.VBox.__init__(self, hexpand=True, vexpand=False)
        GrampsFrame.__init__(
            self, grstate, groptions, primary_obj, secondary_obj=secondary_obj
        )

        self.body = Gtk.HBox(hexpand=True, margin=3)
        if self.secondary and self.secondary.is_reference:
            self.eventbox.add(self.body)
            self.ref_frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
            self.ref_body = Gtk.VBox(hexpand=True, halign=Gtk.Align.END)
            if "ref" in self.groptions.size_groups:
                self.groptions.size_groups["ref"].add_widget(self.ref_body)
            self.ref_eventbox = Gtk.EventBox()
            self.ref_eventbox.add(self.ref_body)
            self.ref_frame.add(self.ref_eventbox)
            view_obj = Gtk.HBox(hexpand=True)
            view_obj.pack_start(self.eventbox, True, True, 0)
            view_obj.pack_start(self.ref_frame, True, True, 0)
            self.frame.add(view_obj)
            self.add(self.frame)
            self.ref_body.pack_start(
                self.get_ref_label(), expand=False, fill=False, padding=0
            )
        else:
            self.frame.add(self.body)
            if self.primary.obj_type == "Family":
                self.add(self.frame)
            else:
                self.eventbox.add(self.frame)
                self.add(self.eventbox)

        self.image = Gtk.Box()
        self.age = None
        self.title = Gtk.HBox(hexpand=True, halign=Gtk.Align.START)
        self.gramps_id = Gtk.HBox(hexpand=True, halign=Gtk.Align.END)
        self.tags = Gtk.FlowBox(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False)
        if "data" in self.groptions.size_groups:
            self.groptions.size_groups["data"].add_widget(self.facts_grid)
        self.extra_grid = Gtk.Grid(
            row_spacing=2,
            column_spacing=6,
            hexpand=True,
            halign=Gtk.Align.START,
        )
        if "extra" in self.groptions.size_groups:
            self.groptions.size_groups["extra"].add_widget(self.facts_grid)
        self.extra_row = 0
        self.metadata = Gtk.VBox(halign=Gtk.Align.END, hexpand=True)
        if "metadata" in self.groptions.size_groups:
            self.groptions.size_groups["metadata"].add_widget(self.metadata)
        self.metadata.pack_start(self.gramps_id, False, False, 0)
        self.partner1 = None
        self.partner2 = None

        self.build_layout()
        self.load_layout()

    def load_layout(self):
        """
        Load standard portions of layout.
        """
        image_mode = self.get_option("image-mode")
        if image_mode:
            if "media" not in self.groptions.option_space:
                self.load_image(image_mode)

        self.load_gramps_id()
        values = self.get_metadata_attributes()
        if values:
            for value in values:
                label = self.make_label(value, left=False)
                self.metadata.pack_start(label, False, False, 0)
        self.load_tags()

    def refresh_layout(self):
        """
        Refresh primary object and reset layout.
        """
        query_method = self.grstate.dbstate.db.method(
            "get_%s_from_handle", self.primary.obj_type
        )
        self.primary.obj = query_method(self.primary.obj.get_handle())
        list(map(self.image.remove, self.image.get_children()))
        list(map(self.title.remove, self.title.get_children()))
        list(map(self.facts_grid.remove, self.facts_grid.get_children()))
        list(map(self.extra_grid.remove, self.extra_grid.get_children()))
        list(map(self.metadata.remove, self.metadata.get_children()))
        list(map(self.tags.remove, self.tags.get_children()))
        self.load_layout()

    def build_layout(self):
        """
        Construct framework for default layout.
        """
        image_mode = self.get_option("image-mode")
        if image_mode and image_mode in [3, 4]:
            self.body.pack_start(
                self.image, expand=False, fill=False, padding=0
            )

        if self.get_option("show-age"):
            self.age = Gtk.VBox(
                margin_right=3,
                margin_left=3,
                margin_top=3,
                margin_bottom=3,
                spacing=2,
            )
            if "age" in self.groptions.size_groups:
                self.groptions.size_groups["age"].add_widget(self.age)
            self.body.pack_start(self.age, expand=False, fill=False, padding=0)

        vcontent = Gtk.VBox()
        self.body.pack_start(vcontent, expand=True, fill=True, padding=0)
        hcontent = Gtk.HBox()
        vcontent.pack_start(hcontent, expand=True, fill=True, padding=0)
        tcontent = Gtk.VBox()
        hcontent.pack_start(tcontent, expand=True, fill=True, padding=0)
        hcontent.pack_start(self.metadata, expand=True, fill=True, padding=0)
        tcontent.pack_start(self.title, expand=True, fill=True, padding=0)
        tsections = Gtk.HBox()
        tcontent.pack_start(tsections, expand=True, fill=True, padding=0)
        tsections.pack_start(self.facts_grid, expand=True, fill=True, padding=0)
        tsections.pack_start(self.extra_grid, expand=True, fill=True, padding=0)
        tbox = Gtk.HBox(hexpand=False, vexpand=False)
        tbox.pack_start(self.tags, False, False, 0)
        vcontent.pack_start(tbox, expand=True, fill=True, padding=0)
        if image_mode in [1, 2]:
            self.body.pack_start(
                self.image, expand=False, fill=False, padding=0
            )

    def load_image(self, image_mode, media_ref=None):
        """
        Load primary image for the object if found.
        """
        large_size = False
        if image_mode in [2, 4]:
            large_size = True
        self.image.add(
            GrampsImageViewFrame(
                self.grstate, self.primary.obj,
                obj_ref=media_ref, size=large_size
            )
        )
        if "image" in self.groptions.size_groups:
            self.groptions.size_groups["image"].add_widget(self.image)

    def add_fact(self, fact, label=None, extra=False):
        """
        Add a simple fact.
        """
        if not extra:
            if label:
                self.facts_grid.attach(label, 0, self.facts_row, 1, 1)
                self.facts_grid.attach(fact, 1, self.facts_row, 1, 1)
            else:
                self.facts_grid.attach(fact, 0, self.facts_row, 2, 1)
            self.facts_row = self.facts_row + 1
        else:
            if label:
                self.extra_grid.attach(label, 0, self.extra_row, 1, 1)
                self.extra_grid.attach(fact, 1, self.extra_row, 1, 1)
            else:
                self.extra_grid.attach(fact, 0, self.extra_row, 2, 1)
            self.extra_row = self.extra_row + 1

    def add_event(self, event, extra=False, reference=None, show_age=False):
        """
        Adds event information in the requested format to the facts section
        of the object view.
        """
        if not event:
            return

        if not extra:
            grid = self.facts_grid
            row = self.facts_row
        else:
            grid = self.extra_grid
            row = self.extra_row

        age = None
        if show_age:
            if reference and reference.date and event and event.date:
                span = Span(reference.date, event.date)
                if span.is_valid():
                    precision = global_config.get(
                        "preferences.age-display-precision"
                    )
                    age = str(span.format(precision=precision))
                if age == "unknown":
                    age = None

        event_format = self.get_option("event-format")
        if event_format in [3, 4, 6]:
            name = event.type.get_abbreviation(
                trans_text=glocale.translation.sgettext
            )
        else:
            name = glocale.translation.sgettext(event.type.xml_str())

        date = glocale.date_displayer.display(event.date)
        place = place_displayer.display_event(self.grstate.dbstate.db, event)

        text = ""
        if event_format in [1, 2, 5]:
            name_label = self.make_label(name)
        else:
            if event_format in [3, 4, 6]:
                text = name

        if date:
            text = "{} {}".format(text, date).strip()

        if event_format in [1, 3]:
            if place:
                text = "{} {} {}".format(text, _("in"), place).strip()

        if reference and age:
            text = "{} {}".format(text, age)

        if event_format in [1, 2]:
            text_label = self.make_label(text)
            grid.attach(name_label, 0, row, 1, 1)
            grid.attach(text_label, 1, row, 1, 1)
            row = row + 1
        elif event_format in [3, 4]:
            text_label = self.make_label(text)
            grid.attach(text_label, 0, row, 1, 1)
            row = self.facts_row + 1
        elif event_format in [5]:
            grid.attach(name_label, 0, row, 1, 1)
            if date:
                if reference and age:
                    date_label = self.make_label("{} {}".format(date, age))
                else:
                    date_label = self.make_label(date)
                grid.attach(date_label, 1, row, 1, 1)
                row = row + 1
            if place:
                place_label = self.make_label(place)
                grid.attach(place_label, 1, row, 1, 1)
                row = row + 1
        elif event_format in [6]:
            if date:
                if reference and age:
                    date_label = self.make_label(
                        "{} {} {}".format(name, date, age)
                    )
                else:
                    date_label = self.make_label("{} {}".format(name, date))
                grid.attach(date_label, 0, row, 1, 1)
                row = row + 1
            if place:
                if not date:
                    place_label = self.make_label("{} {}".format(name, place))
                else:
                    place_label = self.make_label(place)
                grid.attach(place_label, 0, row, 1, 1)
                row = row + 1

        if not extra:
            self.facts_row = row
        else:
            self.extra_row = row

    def load_gramps_id(self):
        """
        Build the gramps id including bookmark and lock indicators as needed.
        """
        list(map(self.gramps_id.remove, self.gramps_id.get_children()))
        label = Gtk.Label(
            use_markup=True,
            label=self.markup.format(escape(self.primary.obj.gramps_id)),
        )
        self.gramps_id.pack_end(label, False, False, 0)
        if self.grstate.config.get("options.global.enable-bookmarks"):
            for bookmark in get_bookmarks(self.grstate.dbstate.db, self.primary.obj_type).get():
                if bookmark == self.primary.obj.get_handle():
                    image = Gtk.Image()
                    image.set_from_icon_name("gramps-bookmark", Gtk.IconSize.BUTTON)
                    self.gramps_id.pack_end(image, False, False, 0)
                    break
        if self.primary.obj.private:
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            self.gramps_id.pack_end(image, False, False, 0)
        self.gramps_id.show_all()

    def get_ref_label(self):
        """
        Build the label for a reference with lock icon if object marked private.
        """
        hbox = Gtk.HBox()
        image = Gtk.Image()
        image.set_from_icon_name("stock_link", Gtk.IconSize.BUTTON)
        hbox.pack_end(image, False, False, 0)
        if self.secondary.obj.private:
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            hbox.pack_end(image, False, False, 0)
        return hbox

    def load_tags(self):
        """
        Build a flowbox with the tags for the object in the requested format.
        """
        list(map(self.tags.remove, self.tags.get_children()))
        tag_mode = self.get_option("tag-format")
        if not tag_mode:
            return
        tag_width = self.get_option("tag-width")
        self.tags.set_min_children_per_line(tag_width)
        self.tags.set_max_children_per_line(tag_width)
        tags = []
        for handle in self.primary.obj.get_tag_list():
            tag = self.grstate.dbstate.db.get_tag_from_handle(handle)
            tags.append(tag)
        if self.grstate.config.get("options.global.sort-tags-by-name"):
            tags.sort(key=lambda x: x.name)
        else:
            tags.sort(key=lambda x: x.priority)
        for tag in tags:
            if tag_mode == 1:
                tag_view = Gtk.Image()
                tag_view.set_from_icon_name("gramps-tag", Gtk.IconSize.BUTTON)
                tag_view.set_tooltip_text(tag.name)
                css = ".image {{ margin: 0px; padding: 0px; background-image: none; background-color: {}; }}".format(
                    tag.color[:7]
                )
                css_class = "image"
            else:
                tag_view = Gtk.Label(label=tag.name)
                css = ".label {{ margin: 0px; padding: 0px; font-size: x-small; color: black; background-color: {}; }}".format(
                    tag.color[:7]
                )
                css_class = "label"
            css = css.encode("utf-8")
            provider = Gtk.CssProvider()
            provider.load_from_data(css)
            context = tag_view.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            context.add_class(css_class)
            eventbox = Gtk.EventBox()
            eventbox.add(tag_view)
            eventbox.connect("button-press-event", self.tag_click, tag.handle)
            self.tags.add(eventbox)
        self.tags.show_all()

    def tag_click(self, obj, event, handle):
        """
        Request page for tag.
        """
        tag = self.grstate.dbstate.db.get_tag_from_handle(handle)
        data = pickle.dumps((self.primary.obj, "Tag", tag))
        return self.grstate.router("context-changed", ("Tag", data))        
                             
    def get_metadata_attributes(self):
        """
        Return a list of values for any user defined metadata attributes.
        """
        values = []
        number = 1
        while number <= 8:
            option = self.get_option(
                "metadata-attribute-{}".format(number),
                full=False,
                keyed=True,
            )
            if (
                option
                and option[0] == "Attribute"
                and len(option) >= 2
                and option[1]
            ):
                for attribute in self.primary.obj.get_attribute_list():
                    if attribute.get_type().xml_str() == option[1]:
                        if attribute.get_value():
                            values.append(attribute.get_value())
                        break
            number = number + 1
        return values

    def build_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click. First action will always be edit,
        then any custom actions of the derived children, then the global actions
        supported for all objects enabled for them.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.action_menu = Gtk.Menu()
            self.action_menu.append(self._edit_object_option())
            self.add_custom_actions()
            if hasattr(self.primary.obj, "attribute_list"):
                self.action_menu.append(self._attributes_option())
            if hasattr(self.primary.obj, "citation_list"):
                self.action_menu.append(
                    self._citations_option(
                        self.primary.obj,
                        self.add_new_citation,
                        self.add_existing_citation,
                        self.remove_citation,
                    )
                )
            if hasattr(self.primary.obj, "note_list"):
                self.action_menu.append(
                    self._notes_option(
                        self.primary.obj,
                        self.add_new_note,
                        self.add_existing_note,
                        self.remove_note,
                    )
                )
            if hasattr(self.primary.obj, "tag_list"):
                self.action_menu.append(self._tags_option())
            if hasattr(self.primary.obj, "urls"):
                self.action_menu.append(self._urls_option())
            self.action_menu.append(self._copy_to_clipboard_option())
            if self.grstate.config.get("options.global.enable-bookmarks"):
                self.action_menu.append(self._bookmark_option())
            self.action_menu.append(self._change_privacy_option())
            self.action_menu.add(Gtk.SeparatorMenuItem())
            if self.primary.obj.change:
                text = "{} {}".format(
                    _("Last changed"),
                    time.strftime(
                        "%x %X", time.localtime(self.primary.obj.change)
                    ),
                )
            else:
                text = _("Never changed")
            label = Gtk.MenuItem(label=text)
            label.set_sensitive(False)
            self.action_menu.append(label)

            self.action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                self.action_menu.popup_at_pointer(event)
            else:
                self.action_menu.popup(
                    None, None, None, None, event.button, event.time
                )

    def add_custom_actions(self):
        """
        For derived objects to inject their own actions into the menu.
        """

    def goto_person(self, _dummy_obj, handle):
        """
        Change active person for the view.
        """
        self.grstate.router("object-changed", ("Person", handle))

    def _attributes_option(self):
        """
        Build the attributes submenu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item("list-add", _("Add an attribute"), self.add_attribute)
        )
        if len(self.primary.obj.get_attribute_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-attribute", _("Remove an attribute"), removemenu
                )
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            attribute_list = []
            for attribute in self.primary.obj.get_attribute_list():
                text = attribute_option_text(attribute)
                attribute_list.append((text, attribute))
            attribute_list.sort(key=lambda x: x[0])
            for text, attribute in attribute_list:
                removemenu.add(
                    menu_item(
                        "list-remove", text, self.remove_attribute, attribute
                    )
                )
                menu.add(
                    menu_item(
                        "gramps-attribute", text, self.edit_attribute, attribute
                    )
                )
        return submenu_item("gramps-attribute", _("Attributes"), menu)

    def add_attribute(self, _dummy_obj):
        """
        Add a new attribute.
        """
        attribute_types = get_attribute_types(
            self.grstate.dbstate.db, self.primary.obj_type
        )
        try:
            if self.primary.obj_type in ["Source", "Citation"]:
                attribute = SrcAttribute()
                EditSrcAttribute(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    attribute,
                    "",
                    attribute_types,
                    self.added_attribute,
                )
            else:
                attribute = Attribute()
                EditAttribute(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    attribute,
                    "",
                    attribute_types,
                    self.added_attribute,
                )
        except WindowActiveError:
            pass

    def added_attribute(self, attribute):
        """
        Save the new attribute to finish adding it.
        """
        if attribute:
            action = "{} {} {} {} {} {}".format(
                _("Added"),
                _("Attribute"),
                attribute.get_type(),
                _("to"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
            self.primary.obj.add_attribute(attribute)
            self.save_object(self.primary.obj, action_text=action)

    def edit_attribute(self, _dummy_obj, attribute):
        """
        Edit an attribute.
        """
        attribute_types = get_attribute_types(
            self.grstate.dbstate.db, self.primary.obj_type
        )
        try:
            if self.primary.obj_type in ["Source", "Citation"]:
                EditSrcAttribute(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    attribute,
                    "",
                    attribute_types,
                    self.edited_attribute,
                )
            else:
                EditAttribute(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    attribute,
                    "",
                    attribute_types,
                    self.edited_attribute,
                )
        except WindowActiveError:
            pass

    def edited_attribute(self, attribute):
        """
        Save the edited attribute.
        """
        if attribute:
            action = "{} {} {} {} {} {}".format(
                _("Updated"),
                _("Attribute"),
                attribute.get_type(),
                _("for"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
            self.save_object(attribute, action_text=action)

    def remove_attribute(self, _dummy_obj, attribute):
        """
        Remove the given attribute from the current object.
        """
        if not attribute:
            return
        text = attribute_option_text(attribute)
        prefix = _(
            "You are about to remove the following attribute from this object:"
        )
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"), "{}\n\n<b>{}</b>\n\n{}".format(prefix, text, confirm)
        ):
            action = "{} {} {} {} {} {}".format(
                _("Deleted"),
                _("Attribute"),
                attribute.get_type(),
                _("from"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
            self.primary.obj.remove_attribute(attribute)
            self.save_object(self.primary.obj, action_text=action)

    def _tags_option(self):
        """
        Build the tags submenu.
        """
        menu = Gtk.Menu()
        tag_add_list = []
        tag_remove_list = []
        for handle in self.grstate.dbstate.db.get_tag_handles():
            tag = self.grstate.dbstate.db.get_tag_from_handle(handle)
            if handle in self.primary.obj.tag_list:
                tag_remove_list.append(tag)
            else:
                tag_add_list.append(tag)
        for tag_list in [tag_add_list, tag_remove_list]:
            if self.grstate.config.get("options.global.sort-tags-by-name"):
                tag_list.sort(key=lambda x: x.name)
            else:
                tag_list.sort(key=lambda x: x.priority)
        if tag_add_list:
            addmenu = Gtk.Menu()
            for tag in tag_add_list:
                addmenu.add(
                    menu_item("list-add", tag.name, self.add_tag, tag.handle)
                )
            menu.add(submenu_item("gramps-tag", _("Add a tag"), addmenu))
        if tag_remove_list:
            removemenu = Gtk.Menu()
            for tag in tag_remove_list:
                removemenu.add(
                    menu_item(
                        "list-remove", tag.name, self.remove_tag, tag.handle
                    )
                )
            menu.add(submenu_item("gramps-tag", _("Remove a tag"), removemenu))
        menu.add(menu_item("gramps-tag", _("Create new tag"), self.new_tag))
        menu.add(
            menu_item("gramps-tag", _("Organize tags"), self.organize_tags)
        )
        return submenu_item("gramps-tag", _("Tags"), menu)

    def new_tag(self, _dummy_obj):
        """
        Create a new tag.
        """
        tag = Tag()
        try:
            EditTag(self.grstate.dbstate.db, self.grstate.uistate, [], tag)
        except WindowActiveError:
            pass

    def organize_tags(self, _dummy_obj):
        """
        Organize tags.
        """
        try:
            OrganizeTagsDialog(
                self.grstate.dbstate.db, self.grstate.uistate, []
            )
        except WindowActiveError:
            pass

    def add_tag(self, _dummy_obj, handle):
        """
        Add the given tag to the current object.
        """
        if not handle:
            return
        action = "{} {} {} {} {}".format(
            _("Added"),
            _("Tag"),
            _("to"),
            self.primary.obj_lang,
            self.primary.obj.get_gramps_id(),
        )
        self.primary.obj.add_tag(handle)
        self.save_object(self.primary.obj, action_text=action)

    def remove_tag(self, _dummy_obj, handle):
        """
        Remove the given tag from the current object.
        """
        if not handle:
            return
        action = "{} {} {} {} {}".format(
            _("Removed"),
            _("Tag"),
            _("from"),
            self.primary.obj_lang,
            self.primary.obj.get_gramps_id(),
        )
        if self.primary.obj.remove_tag(handle):
            self.save_object(self.primary.obj, action_text=action)

    def _urls_option(self):
        """
        Build the urls submenu.
        """
        menu = Gtk.Menu()
        menu.add(menu_item("list-add", _("Add a url"), self.add_url))
        if len(self.primary.obj.get_url_list()) > 0:
            editmenu = Gtk.Menu()
            menu.add(submenu_item("gramps-url", _("Edit a url"), editmenu))
            removemenu = Gtk.Menu()
            menu.add(submenu_item("gramps-url", _("Remove a url"), removemenu))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            url_list = []
            for url in self.primary.obj.get_url_list():
                text = url.get_description()
                if not text:
                    text = url.get_path()
                url_list.append((text, url))
            url_list.sort(key=lambda x: x[0])
            for text, url in url_list:
                editmenu.add(menu_item("gramps-url", text, self.edit_url, url))
                removemenu.add(
                    menu_item("list-remove", text, self.remove_url, url)
                )
                menu.add(menu_item("gramps-url", text, self.launch_url, url))
        return submenu_item("gramps-url", _("Urls"), menu)

    def add_url(self, _dummy_obj, path=None, description=None):
        """
        Add a new url.
        """
        url = Url()
        url.set_type("Web Home")
        if path:
            url.set_path(path)
        if description:
            url.set_description(description)
        try:
            EditUrl(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                "",
                url,
                self.added_url,
            )
        except WindowActiveError:
            pass

    def added_url(self, url):
        """
        Save the new url to finish adding it.
        """
        if not url:
            return
        action = "{} {} {} {} {} {}".format(
            _("Added"),
            _("Url"),
            url.get_path(),
            _("to"),
            self.primary.obj_lang,
            self.primary.obj.get_gramps_id(),
        )
        self.primary.obj.add_url(url)
        self.save_object(self.primary.obj, action_text=action)

    def edit_url(self, _dummy_obj, url):
        """
        Edit a url.
        """
        try:
            EditUrl(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                "",
                url,
                self.edited_url,
            )
        except WindowActiveError:
            pass

    def edited_url(self, url):
        """
        Save the edited url.
        """
        if not url:
            return
        action = "{} {} {} {} {} {}".format(
            _("Updated"),
            _("Url"),
            url.get_path(),
            _("for"),
            self.primary.obj_lang,
            self.primary.obj.get_gramps_id(),
        )
        self.save_object(self.primary.obj, action_text=action)

    def remove_url(self, _dummy_obj, url):
        """
        Remove the given url from the current object.
        """
        if not url:
            return
        text = url.get_path()
        if url.get_description():
            text = "{}\n{}".format(url.get_description(), text)
        prefix = _(
            "You are about to remove the following url from this object:"
        )
        confirm = _("Are you sure you want to continue?")
        if self.confirm_action(
            _("Warning"), "{}\n\n<b>{}</b>\n\n{}".format(prefix, text, confirm)
        ):
            action = "{} {} {} {} {} {}".format(
                _("Deleted"),
                _("Url"),
                url.get_path(),
                _("from"),
                self.primary.obj_lang,
                self.primary.obj.get_gramps_id(),
            )
            if self.primary.obj.remove_url(url):
                self.save_object(self.primary.obj, action_text=action)

    def launch_url(self, _dummy_obj, url):
        """
        Launch a browser for a url.
        """
        if url and url.get_path():
            display_url(url.get_path())

    def _copy_to_clipboard_option(self):
        """
        Build copy to clipboard option.
        """
        image = Gtk.Image.new_from_icon_name("edit-copy", Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(
            always_show_image=True, image=image, label=_("Copy to clipboard")
        )
        item.connect("activate", self.copy_to_clipboard)
        return item

    def copy_to_clipboard(self, _dummy_obj):
        """
        Copy current object to the clipboard.
        """
        self.grstate.router(
            "copy-to-clipboard",
            (self.primary.obj_type, self.primary.obj.get_handle()),
        )

    def _add_new_family_event_option(self):
        """
        Build menu option for adding a new event for a family.
        """
        if self.primary.obj_type == "Family" or self.groptions.family_backlink:
            return menu_item(
                "gramps-event",
                _("Add a new family event"),
                self.add_new_family_event,
            )
        return None

    def add_new_family_event(self, _dummy_obj):
        """
        Add a new event for a family.
        """
        event = Event()
        event.set_type(EventType(EventType.MARRIAGE))
        event_ref = EventRef()
        event_ref.set_role(EventRoleType(EventRoleType.FAMILY))
        if self.primary.obj_type == "Family":
            event_ref.ref = self.primary.obj.handle
        else:
            event_ref.ref = self.groptions.family_backlink
        try:
            EditEventRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                event,
                event_ref,
                self.added_new_family_event,
            )
        except WindowActiveError:
            pass

    def added_new_family_event(self, event_ref, _dummy_var1):
        """
        Finish adding a new event for a family.
        """
        if self.primary.obj_type == "Family":
            family = self.primary.obj
        else:
            family = self.grstate.dbstate.db.get_family_from_handle(
                self.groptions.family_backlink
            )
        event = self.grstate.dbstate.db.get_event_from_handle(event_ref.ref)
        action = "{} {} {} {} {} {}".format(
            _("Added"),
            _("Event"),
            event.get_gramps_id(),
            _("for"),
            _("Family"),
            family.get_gramps_id(),
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            if family.add_event_ref(event_ref):
                self.grstate.dbstate.db.commit_family(family, trans)

    def _add_new_child_to_family_option(self):
        """
        Build menu item for adding a new child to the family.
        """
        if self.primary.obj_type == "Family" or self.groptions.family_backlink:
            return menu_item(
                "gramps-person",
                _("Add a new child to the family"),
                self.add_new_child_to_family,
            )
        return None

    def add_new_child_to_family(self, *_dummy_obj):
        """
        Add a new child to a family. First create the person.
        """
        if self.primary.obj_type == "Family":
            handle = self.primary.obj.get_handle()
            family = self.primary.obj
        else:
            handle = self.groptions.family_backlink
            family = self.grstate.dbstate.db.get_family_from_handle(handle)
        callback = lambda x: self.adding_child_to_family(x, handle)
        child = Person()
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father = self.grstate.dbstate.db.get_person_from_handle(
            family.get_father_handle()
        )
        if father:
            preset_name(father, name)
        else:
            mother = self.grstate.dbstate.db.get_person_from_handle(
                family.get_mother_handle()
            )
            if mother:
                preset_name(mother, name)
        child.set_primary_name(name)
        try:
            EditPerson(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                child,
                callback=callback,
            )
        except WindowActiveError:
            pass

    def adding_child_to_family(self, child, family_handle):
        """
        Second set parental relations.
        """
        child_ref = ChildRef()
        child_ref.ref = child.handle
        callback = lambda x: self.added_child(x, child, family_handle)
        name = name_displayer.display(child)
        try:
            EditChildRef(
                name,
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                child_ref,
                callback
            )
        except WindowActiveError:
            pass

    def added_child(self, child_ref, child, family_handle):
        """
        Finish adding the child to the family.
        """
        family = self.grstate.dbstate.db.get_family_from_handle(family_handle)
        action = "{} {} {} {} {} {}".format(
            _("Added"),
            _("Child"),
            child.get_gramps_id(),
            _("to"),
            _("Family"),
            family.get_gramps_id(),
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            family.add_child_ref(child_ref)
            self.grstate.dbstate.db.commit_family(family, trans)
            child.add_parent_family_handle(family_handle)
            self.grstate.dbstate.db.commit_person(child, trans)

    def _add_existing_child_to_family_option(self):
        """
        Build menu item for adding existing child to the family.
        """
        if self.primary.obj_type == "Family" or self.groptions.family_backlink:
            return menu_item(
                "gramps-person",
                _("Add an existing child to the family"),
                self.add_existing_child_to_family,
            )
        return None

    def add_existing_child_to_family(self, *_dummy_obj):
        """
        Add the child to the family. First select the person.
        """
        select_person = SelectorFactory("Person")
        if self.primary.obj_type == "Family":
            family_handle = self.primary.obj.get_handle()
            family = self.primary.obj
        else:
            family_handle = self.groptions.family_backlink
            family = self.grstate.dbstate.db.get_family_from_handle(family_handle)
        skip_list = [family.get_father_handle(), family.get_mother_handle()]
        skip_list.extend(x.ref for x in family.get_child_ref_list())
        selector = select_person(
            self.grstate.dbstate,
            self.grstate.uistate,
            [],
            _("Select Child"),
            skip=skip_list,
        )
        child = selector.run()
        if child:
            self.adding_child_to_family(child, family_handle)

    def _bookmark_option(self):
        """
        Build bookmark option based on current object state.
        """
        for bookmark in get_bookmarks(self.grstate.dbstate.db, self.primary.obj_type).get():
            if bookmark == self.primary.obj.get_handle():
                return menu_item(
                    "gramps-bookmark-delete", _("Unbookmark"), self.change_bookmark, False
                )
        return menu_item(
            "gramps-bookmark", _("Bookmark"), self.change_bookmark, True
        )

    def change_bookmark(self, _dummy_obj, mode):
        """
        Either bookmark or unbookmark the current object.
        """
        bookmarks = get_bookmarks(self.grstate.dbstate.db, self.primary.obj_type)
        bookmark_list = bookmarks.get()
        if mode:
            if self.primary.obj.get_handle() not in bookmark_list:
                bookmarks.insert(0, self.primary.obj.get_handle())
        else:
            if self.primary.obj.get_handle() in bookmark_list:
                bookmarks.remove(self.primary.obj.get_handle())
        self.load_gramps_id()
