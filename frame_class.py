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
GrampsFrame
"""

# ------------------------------------------------------------------------
#
# Python modules
#
# ------------------------------------------------------------------------
from html import escape
import pickle
import re
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
    EditCitation,
    EditEvent,
    EditEventRef,
    EditFamily,
    EditMedia,
    EditNote,
    EditPerson,
    EditPlace,
    EditRepository,
    EditSource,
    EditSrcAttribute,
    EditUrl
)
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    Attribute,
    ChildRef,
    Citation,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    Family,
    Name,
    Note,
    Person,
    SrcAttribute,
    Source,
    Span,
    Surname,
    Tag,
    Url
)
from gramps.gen.utils.db import preset_name
from gramps.gui.ddtargets import DdTargets
from gramps.gui.display import display_url
from gramps.gui.selectors import SelectorFactory
from gramps.gui.views.tags import OrganizeTagsDialog, EditTag


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsConfig, GrampsImageViewFrame
from frame_utils import get_attribute_types, get_config_option, get_gramps_object_type
from page_layout import ProfileViewLayout


try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

_EDITORS = {
    "Citation": EditCitation,
    "Event": EditEvent,
    "Family": EditFamily,
    "Media": EditMedia,
    "Note": EditNote,
    "Person": EditPerson,
    "Place": EditPlace,
    "Repository": EditRepository,
    "Source": EditSource,
}

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
# GrampsFrame class
#
# ------------------------------------------------------------------------
class GrampsFrame(Gtk.VBox, GrampsConfig):
    """
    The GrampsFrame class provides core methods for constructing the view
    and working with the primary Gramps object it exposes.
    """

    def __init__(self, grstate, context, obj, obj_ref=None, vertical=True, groups=None):
        Gtk.VBox.__init__(self, hexpand=True, vexpand=False)
        GrampsConfig.__init__(self, grstate)
        self.context = context
        self.obj = obj
        self.obj_ref = obj_ref
        self.vertical = vertical
        self.action_menu = None
        self.dnd_drop_targets = []
        self.obj_type, self.dnd_type, self.dnd_icon = get_gramps_object_type(self.obj)
        self.obj_type_lang = glocale.translation.sgettext(self.obj_type)

        if groups:
            self.groups = groups
        else:
            self.groups = {
                "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
                "ref": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            }

        self.body = Gtk.HBox(hexpand=True, margin=3)
        self.eventbox = Gtk.EventBox()
        self.eventbox.connect("button-press-event", self.route_action)
        self.frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        if not obj_ref:
            self.frame.add(self.body)
            if isinstance(self.obj, Family):
                self.add(self.frame)
            else:
                self.eventbox.add(self.frame)
                self.add(self.eventbox)
        else:
            self.eventbox.add(self.body)
            self.ref_frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
            self.ref_body = Gtk.VBox(hexpand=True, halign=Gtk.Align.END)
            if "ref" in self.groups:
                self.groups["ref"].add_widget(self.ref_body)
            self.ref_eventbox = Gtk.EventBox()
            self.ref_eventbox.add(self.ref_body)
            self.ref_frame.add(self.ref_eventbox)
            view_obj = Gtk.HBox(hexpand=True)
            view_obj.pack_start(self.eventbox, True, True, 0)
            view_obj.pack_start(self.ref_frame, True, True, 0)
            self.frame.add(view_obj)
            self.add(self.frame)
            self.ref_body.pack_start(self.get_ref_label(), expand=False, fill=False, padding=0)

        self.image = None
        self.age = None
        self.title = Gtk.HBox(hexpand=True, halign=Gtk.Align.START)
        self.tags = Gtk.HBox(hexpand=True, halign=Gtk.Align.START)
        self.facts_grid = Gtk.Grid(row_spacing=2, column_spacing=6, halign=Gtk.Align.START, hexpand=True)
        if "data" in self.groups:
            self.groups["data"].add_widget(self.facts_grid)
        self.facts_row = 0
        self.extra_grid = Gtk.Grid(row_spacing=2, column_spacing=6, hexpand=True, halign=Gtk.Align.START)
        if "extra" in self.groups:
            self.groups["extra"].add_widget(self.facts_grid)
        self.extra_row = 0
        self.metadata = Gtk.VBox(halign=Gtk.Align.END, hexpand=True)
        if "metadata" in self.groups:
            self.groups["metadata"].add_widget(self.metadata)
        self.partner1 = None
        self.partner2 = None

        self.build_layout()
        self.metadata.pack_start(self.get_gramps_id_label(), expand=False, fill=False, padding=0)
        values = self.get_metadata_attributes()
        if values:
            for value in values:
                label = self.make_label(value, left=False)
                self.metadata.pack_start(label, False, False, 0)

        flowbox = self.get_tags_flowbox()
        if flowbox:
            self.tags.pack_start(flowbox, expand=True, fill=True, padding=0)

    def build_layout(self):
        """
        Construct framework for default layout.
        """
        image_mode = self.option(self.context, "image-mode")
        if image_mode:
            self.load_image(image_mode)
            if image_mode in [3, 4]:
                self.body.pack_start(self.image, expand=False, fill=False, padding=0)

        if self.option(self.context, "show-age"):
            self.age = Gtk.VBox(
                margin_right=3,
                margin_left=3,
                margin_top=3,
                margin_bottom=3,
                spacing=2
            )
            if "age" in self.groups:
                self.groups["age"].add_widget(self.age)
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
        vcontent.pack_start(self.tags, expand=True, fill=True, padding=0)

        if image_mode in [1, 2]:
            self.body.pack_start(self.image, expand=False, fill=False, padding=0)

    def enable_drag(self):
        """
        Enable self as a drag source.
        """
        if self.eventbox:
            self.eventbox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                          [], Gdk.DragAction.COPY)
            target_list = Gtk.TargetList.new([])
            target_list.add(self.dnd_type.atom_drag_type,
                            self.dnd_type.target_flags,
                            self.dnd_type.app_id)
            self.eventbox.drag_source_set_target_list(target_list)
            self.eventbox.drag_source_set_icon_name(self.dnd_icon)
            self.eventbox.connect('drag_data_get', self.drag_data_get)

    def drag_data_get(self, widget, context, sel_data, info, time):
        """
        Return requested data.
        """
        if info == self.dnd_type.app_id:
            data = (self.dnd_type.drag_type, id(self), self.obj.get_handle(), 0)
            sel_data.set(self.dnd_type.atom_drag_type, 8, pickle.dumps(data))

    def enable_drop(self):
        """
        Enable self as a drop target.
        """
        if self.eventbox:
            self.dnd_drop_targets.append(DdTargets.URI_LIST.target())
            for target in DdTargets.all_text_targets():
                self.dnd_drop_targets.append(target)
            self.dnd_drop_targets.append(Gtk.TargetEntry.new('text/html', 0, 7))
            self.dnd_drop_targets.append(Gtk.TargetEntry.new('URL', 0, 8))
            self.dnd_drop_targets.append(DdTargets.NOTE_LINK.target())
            self.dnd_drop_targets.append(DdTargets.CITATION_LINK.target())
            self.eventbox.drag_dest_set(
                Gtk.DestDefaults.ALL,
                self.dnd_drop_targets,
                Gdk.DragAction.COPY
            )
            self.eventbox.connect("drag-data-received", self.on_drag_data_received)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        """
        Handle dropped data.
        """
        if data and data.get_data():
            try:
                dnd_type, obj_id, obj_handle, skip = pickle.loads(data.get_data())
            except pickle.UnpicklingError:
                return self.dropped_text(data.get_data().decode("utf-8"))
            if id(self) == obj_id:
                return
            if DdTargets.CITATION_LINK.drag_type == dnd_type:
                self.added_citation(obj_handle)
            elif DdTargets.NOTE_LINK.drag_type == dnd_type:
                self.added_note(obj_handle)

    def dropped_text(self, data):
        """
        Examine and try to handle dropped text in a reasonable manner.
        """
        added_urls = 0
        if hasattr(self.obj, "urls"):
            links = re.findall(r'(?P<url>https?://[^\s]+)', data)
            if links:
                for link in links:
                    self.add_url(None, path=link)
                    added_urls = added_urls + len(link)
        if not added_urls or (len(data) > (2 * added_urls)):
            if hasattr(self.obj, "note_list"):
                self.add_new_note(None, content=data)

    def load_image(self, image_mode):
        """
        Load primary image for the object if found.
        """
        large_size = False
        if image_mode in [2, 4]:
            large_size = True
        self.image = GrampsImageViewFrame(
            self.grstate,
            self.obj,
            size=large_size
        )
        if self.groups and "image" in self.groups:
            self.groups["image"].add_widget(self.image)

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
                    precision = global_config.get("preferences.age-display-precision")
                    age = str(span.format(precision=precision))
                if age == "unknown":
                    age = None

        event_format = self.option(self.context, "event-format")
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
                    date_label = self.make_label("{} {} {}".format(name, date, age))
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

    def get_gramps_id_label(self):
        """
        Build the label for a gramps id including lock icon if object marked private.
        """
        label = Gtk.Label(use_markup=True, label=self.markup.format(escape(self.obj.gramps_id)))
        hbox = Gtk.HBox()
        hbox.pack_end(label, False, False, 0)
        if self.obj.private:
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            hbox.pack_end(image, False, False, 0)
        return hbox

    def get_ref_label(self):
        """
        Build the label for a reference with lock icon if object marked private.
        """
        hbox = Gtk.HBox()
        image = Gtk.Image()
        image.set_from_icon_name("stock_link", Gtk.IconSize.BUTTON)
        hbox.pack_end(image, False, False, 0)
        if self.obj_ref.private:
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            hbox.pack_end(image, False, False, 0)
        return hbox

    def get_tags_flowbox(self):
        """
        Build a flowbox with the tags for the object in the requested format.
        """
        tag_mode = self.option(self.context, "tag-format")
        if not tag_mode:
            return None
        tag_width = self.option(self.context, "tag-width")
        flowbox = Gtk.FlowBox(
            min_children_per_line=tag_width,
            max_children_per_line=tag_width,
            orientation=Gtk.Orientation.HORIZONTAL
        )
        tags = []
        for handle in self.obj.get_tag_list():
            tag = self.grstate.dbstate.db.get_tag_from_handle(handle)
            tags.append(tag)
        if self.grstate.config.get("options.global.sort-tags-by-name"):
            tags.sort(key = lambda x: x.name)
        else:
            tags.sort(key = lambda x: x.priority)
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
            flowbox.add(tag_view)
        flowbox.show_all()
        return flowbox

    def get_metadata_attributes(self):
        """
        Return a list of values for any user defined metadata attributes.
        """
        values = []
        number = 1
        while number <= 8:
            option = self.option(self.context, "metadata-attribute-{}".format(number), full=False, keyed=True)
            if option and option[0] == "Attribute" and len(option) >= 2 and option[1]:
                for attribute in self.obj.get_attribute_list():
                    if attribute.get_type().xml_str() == option[1]:
                        if attribute.get_value():
                            values.append(attribute.get_value())
                        break
            number = number + 1
        return values

    def route_action(self, obj, event):
        """
        Route the action if the frame was clicked on.
        """
        if button_activated(event, _RIGHT_BUTTON):
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                self.layout_editor()
            else:
                self.build_action_menu(obj, event)
        elif not button_activated(event, _LEFT_BUTTON):
            self.switch_object(None, None, self.obj_type, self.obj.get_handle())

    def layout_editor(self):
        """
        Launch page layout editor.
        """
        try:
            ProfileViewLayout(self.grstate.uistate, self.grstate.config, self.obj_type)
        except WindowActiveError:
            pass

    def build_action_menu(self, obj, event):
        """
        Build the action menu for a right click. First action will always be edit,
        then any custom actions of the derived children, then the global actions
        supported for all objects enabled for them.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.action_menu = Gtk.Menu()
            self.action_menu.append(self._edit_object_option())
            self.add_custom_actions()
            if hasattr(self.obj, "attribute_list"):
                self.action_menu.append(self._attributes_option())
            if hasattr(self.obj, "citation_list"):
                self.action_menu.append(self._citations_option())
            if hasattr(self.obj, "note_list"):
                self.action_menu.append(self._notes_option())
            if hasattr(self.obj, "tag_list"):
                self.action_menu.append(self._tags_option())
            if hasattr(self.obj, "urls"):
                self.action_menu.append(self._urls_option())
            self.action_menu.append(self._copy_to_clipboard_option())
            self.action_menu.append(self._change_privacy_option())
            if self.obj.change:
                text = "{} {}".format(
                    _("Last changed"),
                    time.strftime("%x %X", time.localtime(self.obj.change)),
                )
            else:
                text = _("Never changed")
            label = Gtk.MenuItem(label=text)
            self.action_menu.append(label)

            self.action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                self.action_menu.popup_at_pointer(event)
            else:
                self.action_menu.popup(None, None, None, None, event.button, event.time)

    def add_custom_actions(self):
        """
        For derived objects to inject their own actions into the menu.
        """

    def _menu_item(self, icon, label, callback, data1=None, data2=None):
        """
        Helper for constructing a menu item.
        """
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
        if data2 is not None:
            item.connect("activate", callback, data1, data2)
        elif data1 is not None:
            item.connect("activate", callback, data1)
        else:
            item.connect("activate", callback)
        return item

    def _submenu_item(self, icon, label, menu):
        """
        Helper for constructing a submenu item.
        """
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
        item.set_submenu(menu)
        return item

    def goto_person(self, obj, handle):
        """
        Change active person for the view.
        """
        self.grstate.router('object-changed', ("Person", handle))

    def _edit_object_option(self):
        """
        Build the edit option.
        """
        if self.obj_type == "Person":
            name = "{} {}".format(_("Edit"), name_displayer.display(self.obj))
        else:
            name = "{} {}".format(_("Edit"), self.obj_type.lower())
        return self._menu_item("gtk-edit", name, self.edit_object)

    def edit_object(self, skip=None, obj=None, obj_type=None):
        """
        Launch the desired editor based on object type defaulting to the managed object.
        """
        obj = obj or self.obj
        obj_type = obj_type or self.obj_type
        try:
            _EDITORS[obj_type](self.grstate.dbstate, self.grstate.uistate, [], obj)
        except WindowActiveError:
            pass

    def _attributes_option(self):
        """
        Build the attributes submenu.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("list-add", _("Add an attribute"), self.add_attribute))
        if len(self.obj.get_attribute_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-attribute", _("Remove an attribute"), removemenu))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            attribute_list = []
            for attribute in self.obj.get_attribute_list():
                text = self._attribute_option_text(attribute)
                attribute_list.append((text, attribute))
            attribute_list.sort(key=lambda x: x[0])
            for text, attribute in attribute_list:
                removemenu.add(self._menu_item("list-remove", text, self.remove_attribute, attribute))
                menu.add(self._menu_item("gramps-attribute", text, self.edit_attribute, attribute))
        return self._submenu_item("gramps-attribute", _("Attributes"), menu)

    def _attribute_option_text(self, attribute):
        """
        Helper to build attribute description string.
        """
        text = "{}: {}".format(attribute.get_type(), attribute.get_value())
        if len(text) > 50:
            text = text[:50]+"..."
        return text

    def add_attribute(self, obj):
        """
        Add a new attribute.
        """
        attribute_types = get_attribute_types(self.grstate.dbstate.db, self.obj_type)
        try:
            if self.obj_type in ["Source", "Citation"]:
                attribute = SrcAttribute()
                EditSrcAttribute(self.grstate.dbstate, self.grstate.uistate, [], attribute, "", attribute_types, self.added_attribute)
            else:
                attribute = Attribute()
                EditAttribute(self.grstate.dbstate, self.grstate.uistate, [], attribute, "", attribute_types, self.added_attribute)
        except WindowActiveError:
            pass

    def added_attribute(self, attribute):
        """
        Save the new attribute to finish adding it.
        """
        if attribute:
            action = "{} {} {} {} {}".format(
                _("Added Attribute"),
                attribute.get_type(),
                _("to"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                if self.obj.add_attribute(attribute):
                    commit_method(self.obj, trans)

    def edit_attribute(self, obj, attribute):
        """
        Edit an attribute.
        """
        attribute_types = get_attribute_types(self.grstate.dbstate.db, self.obj_type)
        try:
            if self.obj_type in ["Source", "Citation"]:
                EditSrcAttribute(self.grstate.dbstate, self.grstate.uistate, [], attribute, "", attribute_types, self.edited_attribute)
            else:
                EditAttribute(self.grstate.dbstate, self.grstate.uistate, [], attribute, "", attribute_types, self.edited_attribute)
        except WindowActiveError:
            pass

    def edited_attribute(self, attribute):
        """
        Save the edited attribute.
        """
        if attribute:
            action = "{} {} {} {} {}".format(
                _("Updated Attribute"),
                attribute.get_type(),
                _("for"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                commit_method(self.obj, trans)

    def remove_attribute(self, obj, old_attribute):
        """
        Remove the given attribute from the current object.
        """
        if old_attribute:
            text = self._attribute_option_text(old_attribute)
            prefix = _("You are about to remove the following attribute from this object:")
            confirm = _("Are you sure you want to continue?")
            if self.confirm_action(
                _("Warning"),
                "{}\n\n<b>{}</b>\n\n{}".format(prefix, text, confirm)
            ):
                action = "{} {} {} {} {}".format(
                    _("Deleted Attribute"),
                    old_attribute.get_type(),
                    _("from"),
                    self.obj_type_lang,
                    self.obj.get_gramps_id()
                )
                commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(action, self.grstate.dbstate.db) as trans:
                    if self.obj.remove_attribute(old_attribute):
                        commit_method(self.obj, trans)

    def _citations_option(self):
        """
        Build the citations submenu.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("list-add", _("Add a new citation"), self.add_new_citation))
        menu.add(self._menu_item("list-add", _("Add an existing citation"), self.add_existing_citation))
        if len(self.obj.get_citation_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-citation", _("Remove a citation"), removemenu))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            citation_list = []
            for handle in self.obj.get_citation_list():
                citation = self.grstate.dbstate.db.get_citation_from_handle(handle)
                text = self._citation_option_text(citation)
                citation_list.append((text, citation))
            citation_list.sort(key=lambda x: x[0])
            for text, citation in citation_list:
                removemenu.add(self._menu_item("list-remove", text, self.remove_citation, citation))
                menu.add(self._menu_item("gramps-citation", text, self.edit_citation, citation))
        return self._submenu_item("gramps-citation", _("Citations"), menu)

    def _citation_option_text(self, citation):
        """
        Helper to build citation description string.
        """
        if citation.source_handle:
            source = self.grstate.dbstate.db.get_source_from_handle(citation.source_handle)
            if source.get_title():
                text = source.get_title()
            else:
                text = "[{}]".format(_("Missing Source"))
        if citation.page:
            text = "{}: {}".format(text, citation.page)
        else:
            text = "{}: [{}]".format(text, _("Missing Page"))
        return text

    def add_new_citation(self, obj):
        """
        Add a new citation.
        """
        citation = Citation()
        source = Source()
        try:
            EditCitation(self.grstate.dbstate, self.grstate.uistate, [], citation, source, self.added_citation)
        except WindowActiveError:
            pass

    def added_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle:
            citation = self.grstate.dbstate.db.get_citation_from_handle(handle)
            action = "{} {} {} {} {}".format(
                _("Added Citation"),
                citation.get_gramps_id(),
                _("to"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                if self.obj.add_citation(handle):
                    commit_method(self.obj, trans)

    def add_existing_citation(self, obj):
        """
        Add an existing citation.
        """
        select_citation = SelectorFactory('Citation')
        selector = select_citation(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            if isinstance(selection, Source):
                try:
                    EditCitation(self.grstate.dbstate, self.grstate.uistate, [],
                                 Citation(), selection,
                                 callback=self.added_citation)
                except WindowActiveError:
                    pass
            elif isinstance(selection, Citation):
                try:
                    EditCitation(self.grstate.dbstate, self.grstate.uistate, [],
                                 selection, callback=self.added_citation)
                except WindowActiveError:
                    pass
            else:
                raise ValueError("Selection must be either source or citation")

    def edit_citation(self, obj, citation):
        """
        Edit a citation.
        """
        self.edit_object(None, citation, "Citation")

    def remove_citation(self, obj, old_citation):
        """
        Remove the given citation from the current object.
        """
        if old_citation:
            text = self._citation_option_text(old_citation)
            prefix = _("You are about to remove the following citation from this object:")
            extra = _("Note this only removes the reference and does not delete the actual citation. " \
                      "The citation could be added back unless permanently deleted elsewhere.")
            confirm = _("Are you sure you want to continue?")
            if self.confirm_action(
                _("Warning"),
                "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm)
            ):
                action = "{} {} {} {} {}".format(
                    _("Removed Citation"),
                    old_citation.get_gramps_id(),
                    _("from"),
                    self.obj_type_lang,
                    self.obj.get_gramps_id()
                )
                commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(action, self.grstate.dbstate.db) as trans:
                    if self.obj.citation_list.remove(old_citation.get_handle()):
                        commit_method(self.obj, trans)

    def _notes_option(self):
        """
        Build the notes submenu.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("list-add", _("Add a new note"), self.add_new_note))
        menu.add(self._menu_item("list-add", _("Add an existing note"), self.add_existing_note))
        if len(self.obj.get_note_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-notes", _("Remove a note"), removemenu))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            note_list = []
            for handle in self.obj.get_note_list():
                note = self.grstate.dbstate.db.get_note_from_handle(handle)
                text = self._note_option_text(note)
                note_list.append((text, note))
            note_list.sort(key=lambda x: x[0])
            for text, note in note_list:
                removemenu.add(self._menu_item("list-remove", text, self.remove_note, note))
                menu.add(self._menu_item("gramps-notes", text, self.edit_note, note.handle))
        if self.option("page", "include-child-notes"):
                note_list = []
                for child_obj in self.obj.get_note_child_list():
                    for handle in child_obj.get_note_list():
                        note = self.grstate.dbstate.db.get_note_from_handle(handle)
                        text = self._note_option_text(note)
                        note_list.append((text, note))
                if len(note_list) > 0:
                    menu.add(Gtk.SeparatorMenuItem())
                    menu.add(Gtk.SeparatorMenuItem())
                    note_list.sort(key=lambda x: x[0])
                    for text, note in note_list:
                        menu.add(self._menu_item("gramps-notes", text, self.edit_note, note.handle))
        return self._submenu_item("gramps-notes", _("Notes"), menu)

    def _note_option_text(self, note):
        """
        Helper to build note description string.
        """
        notetype = str(note.get_type())
        text = note.get()[:50].replace('\n', ' ')
        if len(text) > 40:
            text = text[:40]+"..."
        return "{}: {}".format(notetype, text)

    def add_new_note(self, obj, content=None):
        """
        Add a new note.
        """
        note = Note()
        if content:
            note.set(content)
        try:
            EditNote(self.grstate.dbstate, self.grstate.uistate, [], note, self.added_note)
        except WindowActiveError:
            pass

    def added_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle:
            note = self.grstate.dbstate.db.get_note_from_handle(handle)
            action = "{} {} {} {} {}".format(
                _("Added Note"),
                note.get_gramps_id(),
                _("to"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                if self.obj.add_note(handle):
                    commit_method(self.obj, trans)

    def add_existing_note(self, obj):
        """
        Add an existing note.
        """
        select_note = SelectorFactory('Note')
        selector = select_note(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            self.added_note(selection.handle)

    def edit_note(self, obj, handle):
        """
        Edit a note.
        """
        note = self.grstate.dbstate.db.get_note_from_handle(handle)
        self.edit_object(None, note, "Note")

    def remove_note(self, obj, old_note):
        """
        Remove the given note from the current object.
        """
        if old_note:
            text = self._note_option_text(old_note)
            prefix = _("You are about to remove the following note from this object:")
            extra = _("Note this only removes the reference and does not delete the actual note. " \
                      "The note could be added back unless permanently deleted elsewhere.")
            confirm = _("Are you sure you want to continue?")
            if self.confirm_action(
                _("Warning"),
                "{}\n\n<b>{}</b>\n\n{}\n\n{}".format(prefix, text, extra, confirm)
            ):
                action = "{} {} {} {} {}".format(
                    _("Removed Note"),
                    old_note.get_gramps_id(),
                    _("from"),
                    self.obj_type_lang,
                    self.obj.get_gramps_id()
                )
                commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(action, self.grstate.dbstate.db) as trans:
                    if self.obj.note_list.remove(old_note.get_handle()):
                        commit_method(self.obj, trans)

    def _tags_option(self):
        """
        Build the tags submenu.
        """
        menu = Gtk.Menu()
        tag_add_list = []
        tag_remove_list = []
        for handle in self.grstate.dbstate.db.get_tag_handles():
            tag = self.grstate.dbstate.db.get_tag_from_handle(handle)
            if handle in self.obj.tag_list:
                tag_remove_list.append(tag)
            else:
                tag_add_list.append(tag)
        for tag_list in [tag_add_list, tag_remove_list]:
            if self.option("page", "sort-tags-by-name"):
                tag_list.sort(key = lambda x: x.name)
            else:
                tag_list.sort(key = lambda x: x.priority)
        if tag_add_list:
            addmenu = Gtk.Menu()
            for tag in tag_add_list:
                addmenu.add(self._menu_item("list-add", tag.name, self.add_tag, tag.handle))
            menu.add(self._submenu_item("gramps-tag", _("Add a tag"), addmenu))
        if tag_remove_list:
            removemenu = Gtk.Menu()
            for tag in tag_remove_list:
                removemenu.add(self._menu_item("list-remove", tag.name, self.remove_tag, tag.handle))
            menu.add(self._submenu_item("gramps-tag", _("Remove a tag"), removemenu))
        menu.add(self._menu_item("gramps-tag", _("Create new tag"), self.new_tag))
        menu.add(self._menu_item("gramps-tag", _("Organize tags"), self.organize_tags))
        return self._submenu_item("gramps-tag", _("Tags"), menu)

    def new_tag(self, obj):
        """
        Create a new tag.
        """
        tag = Tag()
        try:
            EditTag(self.grstate.dbstate.db, self.grstate.uistate, [], tag)
        except WindowActiveError:
            pass

    def organize_tags(self, obj):
        """
        Organize tags.
        """
        try:
            OrganizeTagsDialog(self.grstate.dbstate.db, self.grstate.uistate, [])
        except WindowActiveError:
            pass

    def add_tag(self, obj, handle):
        """
        Add the given tag to the current object.
        """
        if handle:
            action = "{} {} {} {}".format(
                _("Added Tag"),
                _("to"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.obj.add_tag(handle)
                commit_method(self.obj, trans)

    def remove_tag(self, obj, handle):
        """
        Remove the given tag from the current object."
        """
        if handle:
            action = "{} {} {} {}".format(
                _("Removed Tag"),
                _("from"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                if self.obj.remove_tag(handle):
                    commit_method(self.obj, trans)

    def _urls_option(self):
        """
        Build the urls submenu.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("list-add", _("Add a url"), self.add_url))
        if len(self.obj.get_url_list()) > 0:
            editmenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-url", _("Edit a url"), editmenu))
            removemenu = Gtk.Menu()
            menu.add(self._submenu_item("gramps-url", _("Remove a url"), removemenu))
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            url_list = []
            for url in self.obj.get_url_list():
                text = url.get_description()
                if not text:
                    text = url.get_path()
                url_list.append((text, url))
            url_list.sort(key=lambda x: x[0])
            for text, url in url_list:
                editmenu.add(self._menu_item("gramps-url", text, self.edit_url, url))
                removemenu.add(self._menu_item("list-remove", text, self.remove_url, url))
                menu.add(self._menu_item("gramps-url", text, self.launch_url, url))
        return self._submenu_item("gramps-url", _("Urls"), menu)

    def add_url(self, obj, path=None, description=None):
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
            EditUrl(self.grstate.dbstate, self.grstate.uistate, [], "", url, self.added_url)
        except WindowActiveError:
            pass

    def added_url(self, url):
        """
        Save the new url to finish adding it.
        """
        if url:
            action = "{} {} {} {} {}".format(
                _("Added Url"),
                url.get_path(),
                _("to"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                self.obj.add_url(url)
                commit_method(self.obj, trans)

    def edit_url(self, obj, url):
        """
        Edit a url.
        """
        if url:
            try:
                EditUrl(self.grstate.dbstate, self.grstate.uistate, [], "", url, self.edited_url)
            except WindowActiveError:
                pass

    def edited_url(self, url):
        """
        Save the edited url.
        """
        if url:
            action = "{} {} {} {} {}".format(
                _("Updated Url"),
                url.get_path(),
                _("for"),
                self.obj_type_lang,
                self.obj.get_gramps_id()
            )
            commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(action, self.grstate.dbstate.db) as trans:
                commit_method(self.obj, trans)

    def remove_url(self, obj, old_url):
        """
        Remove the given url from the current object.
        """
        if old_url:
            text = old_url.get_path()
            if old_url.get_description():
                text = "{}\n{}".format(old_url.get_description(), text)
            prefix = _("You are about to remove the following url from this object:")
            confirm = _("Are you sure you want to continue?")
            if self.confirm_action(
                _("Warning"),
                "{}\n\n<b>{}</b>\n\n{}".format(prefix, text, confirm)
            ):
                action = "{} {} {} {} {}".format(
                    _("Deleted Url"),
                    old_url.get_path(),
                    _("from"),
                    self.obj_type_lang,
                    self.obj.get_gramps_id()
                )
                commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(action, self.grstate.dbstate.db) as trans:
                    if self.obj.remove_url(old_url):
                        commit_method(self.obj, trans)

    def launch_url(self, obj, url):
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

    def copy_to_clipboard(self, obj):
        """
        Copy current object to the clipboard.
        """
        self.grstate.router('copy-to-clipboard', (self.obj_type, self.obj.get_handle()))

    def _change_privacy_option(self):
        """
        Build privacy option based on current object state.
        """
        if self.obj.private:
            return self._menu_item("gramps-unlock", _("Make public"), self.change_privacy, False)
        return self._menu_item("gramps-lock", _("Make private"), self.change_privacy, True)

    def change_privacy(self, obj, mode):
        """
        Update the privacy indicator for the current object.
        """
        if mode:
            text = _("Private")
        else:
            text = _("Public")
        action = "{} {} {} {}".format(
            _("Made"),
            self.obj_type_lang,
            self.obj.get_gramps_id(),
            text
        )
        commit_method = self.grstate.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            self.obj.set_privacy(mode)
            commit_method(self.obj, trans)

    def _add_new_family_event_option(self):
        """
        Build menu option for adding a new event for a family.
        """
        if self.obj_type == "Family" or self.family_backlink:
            return self._menu_item("gramps-event", _("Add a new family event"), self.add_new_family_event)
        return None

    def add_new_family_event(self, obj):
        """
        Add a new event for a family.
        """
        event = Event()
        event.set_type(EventType(EventType.MARRIAGE))
        event_ref = EventRef()
        event_ref.set_role(EventRoleType(EventRoleType.FAMILY))
        if self.obj_type == "Family":
            event_ref.ref = self.obj.handle
        else:
            event_ref.ref = self.family_backlink
        try:
            EditEventRef(
                self.grstate.dbstate, self.grstate.uistate, [], event, event_ref, self.added_new_family_event
            )
        except WindowActiveError:
            pass

    def added_new_family_event(self, event_ref, primary):
        """
        Finish adding a new event for a family.
        """
        if self.obj_type == "Family":
            family = self.obj
        else:
            family = self.grstate.dbstate.db.get_family_from_handle(self.family_backlink)
        event = self.grstate.dbstate.db.get_event_from_handle(event_ref.ref)
        action = "{} {} {} {} {}".format(
            _("Added Event"),
            event.get_gramps_id(),
            _("for"),
            _("Family"),
            family.get_gramps_id()
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            if family.add_event_ref(event_ref):
                self.grstate.dbstate.db.commit_family(family, trans)

    def _add_new_child_to_family_option(self):
        """
        Build menu item for adding a new child to the family.
        """
        if self.obj_type == "Family" or self.family_backlink:
            return self._menu_item("gramps-person", _("Add a new child to the family"), self.add_new_child_to_family)
        return None

    def add_new_child_to_family(self, *obj):
        """
        Add a new child to a family.
        """
        if self.obj_type == "Family":
            handle = self.obj.handle
            family = self.obj
        else:
            handle = self.family_backlink
            family = self.grstate.dbstate.db.get_family_from_handle(handle)
        callback = lambda x: self.added_child(x, handle)
        person = Person()
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father = self.grstate.dbstate.db.get_person_from_handle(family.get_father_handle())
        if father:
            preset_name(father, name)
        else:
            mother = self.grstate.dbstate.db.get_person_from_handle(family.get_mother_handle())
            if mother:
                preset_name(mother, name)
        person.set_primary_name(name)
        try:
            EditPerson(self.grstate.dbstate, self.grstate.uistate, [], person, callback=callback)
        except WindowActiveError:
            pass

    def added_child(self, person, family_handle):
        """
        Finish adding the child to the family.
        """
        ref = ChildRef()
        ref.ref = person.get_handle()
        family = self.grstate.dbstate.db.get_family_from_handle(family_handle)
        action = "{} {} {} {} {}".format(
            _("Added Child"),
            person.get_gramps_id(),
            _("to"),
            _("Family"),
            family.get_gramps_id()
        )
        with DbTxn(action, self.grstate.dbstate.db) as trans:
            family.add_child_ref(ref)
            person.add_parent_family_handle(family_handle)
            self.grstate.dbstate.db.commit_person(person, trans)
            self.grstate.dbstate.db.commit_family(family, trans)

    def _add_existing_child_to_family_option(self):
        """
        Build menu item for adding existing child to the family.
        """
        if self.obj_type == "Family" or self.family_backlink:
            return self._menu_item("gramps-person", _("Add an existing child to the family"), self.add_existing_child_to_family)
        return None

    def add_existing_child_to_family(self, *obj):
        """
        Add the child to the family.
        """
        select_person = SelectorFactory("Person")
        if self.obj_type == "Family":
            family = self.obj
            handle = self.obj.handle
        else:
            handle = self.family_backlink
            family = self.grstate.dbstate.db.get_family_from_handle(handle)
        # it only makes sense to skip those who are already in the family
        skip_list = [family.get_father_handle(), family.get_mother_handle()]
        skip_list.extend(x.ref for x in family.get_child_ref_list())
        selector = select_person(
            self.grstate.dbstate, self.grstate.uistate, [], _("Select Child"), skip=skip_list
        )
        person = selector.run()
        if person:
            self.added_child(person, handle)

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("options.global.border-width")
        color = self.get_color_css()
        css = ".frame {{ border-width: {}px; {} }}".format(border, color)
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")

    def get_color_css(self):
        """
        For derived objects to set their color scheme if in use.
        """
        return ""
