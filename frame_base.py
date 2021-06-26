#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
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
    EditCitation,
    EditEvent,
    EditEventRef,
    EditFamily,
    EditNote,
    EditPerson,
    EditPlace,
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
    Place,
    Repository,
    SrcAttribute,
    Source,
    Span,
    Surname,
    Tag,
    Url
)
from gramps.gen.utils.db import preset_name
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gui.ddtargets import DdTargets
from gramps.gui.display import display_url
from gramps.gui.selectors import SelectorFactory
from gramps.gui.utils import open_file_with_default_application
from gramps.gui.views.tags import OrganizeTagsDialog, EditTag


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

_EDITORS = {
    "Citation": EditCitation,
    "Event": EditEvent,
    "Family": EditFamily,
    "Note": EditNote,
    "Person": EditPerson,
    "Place": EditPlace,
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
# GrampsConfig class
#
# ------------------------------------------------------------------------
class GrampsConfig:
    """
    The GrampsConfig class provides the basis for handling configuration
    related information and helper methods common to both the GrampsFrame
    and the various GrampsFrameGroup classes.
    """

    def __init__(self, dbstate, uistate, space, config):
        self.dbstate = dbstate
        self.uistate = uistate
        self.space = space
        self.context = ""
        self.config = config
        self.enable_tooltips = self.config.get(
            "{}.layout.enable-tooltips".format(self.space)
        )
        self.markup = "{}"
        if self.config.get("{}.layout.use-smaller-detail-font".format(self.space)):
            self.markup = "<small>{}</small>"

    def option(self, context, name):
        """
        Fetches an option from the given context in a configuration name space.
        """
        try:
            return self.config.get("{}.{}.{}".format(self.space, context, name))
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
                justify=Gtk.Justification.LEFT,
                wrap=True,
            )
        else:
            label = Gtk.Label(
                hexpand=False,
                halign=Gtk.Align.END,
                justify=Gtk.Justification.RIGHT,
                wrap=True,
            )
        label.set_markup(self.markup.format(text.replace('&', '&amp;')))
        return label

    def confirm_action(self, title, message):
        """
        If enabled display message and confirm a user requested action.
        """
        if not self.config.get(
            "{}.layout.enable-warnings".format(self.space)
        ):
            return True
        dialog = Gtk.Dialog(parent=self.uistate.window)
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

    def __init__(self, dbstate, uistate, router, space, config, obj, context, eventbox=True):
        Gtk.VBox.__init__(self, hexpand=True, vexpand=False)
        GrampsConfig.__init__(self, dbstate, uistate, space, config)
        self.obj = obj
        self.router = router
        self.context = context
        self.image = None
        self.facts_grid = Gtk.Grid(row_spacing=2, column_spacing=6)
        self.facts_row = 0
        self.action_menu = None
        self.eventbox = None
        self.dnd_type = None
        self.dnd_icon = None

        self.body = Gtk.HBox()
        self.frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        self.frame.add(self.body)        
        if eventbox:
            self.eventbox = Gtk.EventBox()
            self.eventbox.add(self.frame)
            self.eventbox.connect("button-press-event", self.route_action)
            self.add(self.eventbox)
        else:
            self.add(self.frame)

        if isinstance(self.obj, Person):
            self.obj_type = "Person"
            self.dnd_type = DdTargets.PERSON_LINK
            self.dnd_icon = 'gramps-person'
        elif isinstance(self.obj, Family):
            self.obj_type = "Family"
            self.dnd_type = DdTargets.FAMILY_LINK
            self.dnd_icon = 'gramps-family'
        elif isinstance(self.obj, Event):
            self.obj_type = "Event"
            self.dnd_type = DdTargets.EVENT
            self.dnd_icon = 'gramps-event'
        elif isinstance(self.obj, Place):
            self.obj_type = "Place"
        elif isinstance(self.obj, Source):
            self.obj_type = "Source"
        elif isinstance(self.obj, Citation):
            self.obj_type = "Citation"
            self.dnd_type = DdTargets.CITATION_LINK
            self.dnd_icon = 'gramps-citation'
        elif isinstance(self.obj, Repository):
            self.obj_type = "Repository"
        elif isinstance(self.obj, Note):
            self.obj_type = "Note"

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
        
    def load_image(self, groups=None):
        """
        Load primary image for the object if found.
        """
        self.image = ImageFrame(
            self.dbstate,
            self.uistate,
            self.obj,
            size=bool(self.option(self.context, "show-image-large")),
        )
        if groups and "image" in groups:
            groups["image"].add_widget(self.image)

    def add_event(self, event, reference=None, show_age=False):
        """
        Adds event information in the requested format to the facts section
        of the object view.
        """
        if event:
            age = None
            if show_age:
                if reference and reference.date and event and event.date:
                    span = Span(reference.date, event.date)
                    if span.is_valid():
                        precision = global_config.get("preferences.age-display-precision")
                        age = str(span.format(precision=precision))
                    if age == "unknown":
                        age = None

            event_format = self.config.get(
                "{}.{}.event-format".format(self.space, self.context)
            )
            if event_format in [3, 4, 6]:
                name = event.type.get_abbreviation(
                    trans_text=glocale.translation.sgettext
                )
            else:
                name = glocale.translation.sgettext(event.type.xml_str())

            date = glocale.date_displayer.display(event.date)
            place = place_displayer.display_event(self.dbstate.db, event)

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
                self.facts_grid.attach(name_label, 0, self.facts_row, 1, 1)
                self.facts_grid.attach(text_label, 1, self.facts_row, 1, 1)
                self.facts_row = self.facts_row + 1
            elif event_format in [3, 4]:
                text_label = self.make_label(text)
                self.facts_grid.attach(text_label, 0, self.facts_row, 1, 1)
                self.facts_row = self.facts_row + 1
            elif event_format in [5]:
                self.facts_grid.attach(name_label, 0, self.facts_row, 1, 1)
                if date:
                    if reference and age:
                        date_label = self.make_label("{} {}".format(date, age))
                    else:
                        date_label = self.make_label(date)
                    self.facts_grid.attach(date_label, 1, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1
                if place:
                    place_label = self.make_label(place)
                    self.facts_grid.attach(place_label, 1, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1
            elif event_format in [6]:
                if date:
                    if reference and age:
                        date_label = self.make_label("{} {} {}".format(name, date, age))
                    else:
                        date_label = self.make_label("{} {}".format(name, date))
                    self.facts_grid.attach(date_label, 0, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1
                if place:
                    if not date:
                        place_label = self.make_label("{} {}".format(name, place))
                    else:
                        place_label = self.make_label(place)
                    self.facts_grid.attach(place_label, 0, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1

    def get_gramps_id_label(self):
        """
        Build the label for a gramps id including lock icon if object marked private.
        """
        label = Gtk.Label(use_markup=True, label=self.markup.format(self.obj.gramps_id.replace('&', '&amp;')))
        hbox = Gtk.HBox()
        hbox.pack_end(label, False, False, 0)
        if self.obj.private:
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
            min_children_per_line=tag_width, max_children_per_line=tag_width
        )
        tags = []
        for handle in self.obj.get_tag_list():
            tag = self.dbstate.db.get_tag_from_handle(handle)
            tags.append(tag)
        if self.option("layout", "sort-tags-by-name"):
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

    def route_action(self, obj, event):
        """
        Route the action if the frame was clicked on.
        """
        if button_activated(event, _RIGHT_BUTTON):
            self.build_action_menu(obj, event)
        elif button_activated(event, _LEFT_BUTTON):
            self.build_view_menu(obj, event)

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

    def build_view_menu(self, obj, event):
        """
        For derived objects that may wish to provide an action for a left click.
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
        self.router(None, None, handle, "link-person")

    def _edit_object_option(self):
        """
        Build the edit option.
        """
        if self.obj_type == "Person":
            name = _("Edit %s") % name_displayer.display(self.obj)
        else:
            name = _("Edit {}".format(self.obj_type.lower()))
        return self._menu_item("gtk-edit", name, self.edit_object)

    def edit_object(self, skip, obj=None, obj_type=None):
        """
        Launch the desired editor based on object type defaulting to the managed object.
        """
        obj = obj or self.obj
        obj_type = obj_type or self.obj_type
        try:
            _EDITORS[obj_type](self.dbstate, self.uistate, [], obj)
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

    def _get_attribute_types(self):
        """
        Get the available attribute types based on current object type.
        """
        if self.obj_type == "Person":
            return self.dbstate.db.get_person_attribute_types()
        if self.obj_type == "Family":
            return self.dbstate.db.get_family_attribute_types()
        if self.obj_type == "Event":
            return self.dbstate.db.get_event_attribute_types()
        if self.obj_type == "Media":
            return self.dbstate.db.get_media_attribute_types()
        if self.obj_type == "Source":
            return self.dbstate.db.get_source_attribute_types()
        if self.obj_type == "Citation":
            return self.dbstate.db.get_source_attribute_types()
        
    def add_attribute(self, obj):
        """
        Add a new attribute.
        """
        if self.obj_type in ["Source", "Citation"]:
            attribute = SrcAttribute()
        else:
            attribute = Attribute()
        attribute_types = self._get_attribute_types()
        try:
            if self.obj_type in ["Source", "Citation"]:
                EditSrcAttribute(self.dbstate, self.uistate, [], attribute, "", attribute_types, self.added_attribute)
            else:
                EditAttribute(self.dbstate, self.uistate, [], attribute, "", attribute_types, self.added_attribute)
        except WindowActiveError:
            pass
        
    def added_attribute(self, attribute):
        """
        Save the new attribute to finish adding it.
        """
        if attribute:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Attribute to %s") % self.obj_type, self.dbstate.db) as trans:
                self.obj.add_attribute(attribute)
                commit_method(self.obj, trans)

    def edit_attribute(self, obj, attribute):
        """
        Edit an attribute.
        """
        attribute_types = self._get_attribute_types()
        try:
            if self.obj_type in ["Source", "Citation"]:
                EditSrcAttribute(self.dbstate, self.uistate, [], attribute, "", attribute_types, self.edited_attribute)
            else:
                EditAttribute(self.dbstate, self.uistate, [], attribute, "", attribute_types, self.edited_attribute)
        except WindowActiveError:
            pass

    def edited_attribute(self, attribute):
        """
        Save the edited attribute.
        """
        if attribute:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Updated Attribute for %s") % self.obj_type, self.dbstate.db) as trans:
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
                new_list = []
                for attribute in self.obj.get_attribute_list():
                    if not attribute.is_equal(old_attribute):
                        new_list.append(attribute)
                commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(_("Remove Attribute from %s") % self.obj_type, self.dbstate.db) as trans:
                    self.obj.set_attribute_list(new_list)
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
                citation = self.dbstate.db.get_citation_from_handle(handle)
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
            source = self.dbstate.db.get_source_from_handle(citation.source_handle)
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
            EditCitation(self.dbstate, self.uistate, [], citation, source, self.added_citation)
        except WindowActiveError:
            pass
        
    def added_citation(self, handle):
        """
        Add the new or existing citation to the current object.
        """
        if handle:
            self.obj.add_citation(handle)
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Citation to %s") % self.obj_type, self.dbstate.db) as trans:
                commit_method(self.obj, trans)

    def add_existing_citation(self, obj):
        """
        Add an existing citation.
        """
        SelectCitation = SelectorFactory('Citation')
        selector = SelectCitation(self.dbstate, self.uistate, [])
        selection = selector.run()
        if selection:
            if isinstance(selection, Source):
                try:
                    EditCitation(self.dbstate, self.uistate, [],
                                 Citation(), selection,
                                 callback=self.added_citation)
                except WindowActiveError:
                    pass
#                    WarningDialog(_("Cannot share this reference"),
#                                  self.__blocked_text(),
#                                  parent=self.uistate.window)
            elif isinstance(selection, Citation):
                try:
                    EditCitation(self.dbstate, self.uistate, [],
                                 selection, callback=self.added_citation)
                except WindowActiveError:
                    pass
#                    WarningDialog(_("Cannot share this reference"),
#                                  self.__blocked_text(),
#                                  parent=self.uistate.window)
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
                self.obj.citation_list.remove(old_citation.get_handle())
                commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(_("Remove Citation from %s") % self.obj_type, self.dbstate.db) as trans:
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
                note = self.dbstate.db.get_note_from_handle(handle)
                text = self._note_option_text(note)
                note_list.append((text, note))
            note_list.sort(key=lambda x: x[0])            
            for text, note in note_list:
                removemenu.add(self._menu_item("list-remove", text, self.remove_note, note))
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
        
    def add_new_note(self, obj):
        """
        Add a new note.
        """
        note = Note()
        try:
            EditNote(self.dbstate, self.uistate, [], note, self.added_note)
        except WindowActiveError:
            pass
        
    def added_note(self, handle):
        """
        Add the new or existing note to the current object.
        """
        if handle:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Note to %s") % self.obj_type, self.dbstate.db) as trans:
                self.obj.add_note(handle)
                commit_method(self.obj, trans)

    def add_existing_note(self, obj):
        """
        Add an existing note.
        """
        SelectNote = SelectorFactory('Note')
        selector = SelectNote(self.dbstate, self.uistate, [])
        selection = selector.run()
        if selection:
            self.added_note(selection.handle)
        
    def edit_note(self, obj, handle):
        """
        Edit a note.
        """
        note = self.dbstate.db.get_note_from_handle(handle)
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
                self.obj.note_list.remove(old_note.get_handle())
                commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(_("Add Note to %s") % self.obj_type, self.dbstate.db) as trans:
                    commit_method(self.obj, trans)

    def _tags_option(self):
        """
        Build the tags submenu.
        """
        menu = Gtk.Menu()
        tag_add_list = []
        tag_remove_list = []
        for handle in self.dbstate.db.get_tag_handles():
            tag = self.dbstate.db.get_tag_from_handle(handle)
            if handle in self.obj.tag_list:
                tag_remove_list.append(tag)
            else:
                tag_add_list.append(tag)
        for tag_list in [tag_add_list, tag_remove_list]:
            if self.option("layout", "sort-tags-by-name"):
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
            EditTag(self.dbstate.db, self.uistate, [], tag)
        except WindowActiveError:
            pass

    def organize_tags(self, obj):
        """
        Organize tags.
        """
        try:
            OrganizeTagsDialog(self.dbstate.db, self.uistate, [])
        except WindowActiveError:
            pass

    def add_tag(self, obj, handle):
        """
        Add the given tag to the current object.
        """
        commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(_("Add Tag to %s") % self.obj_type, self.dbstate.db) as trans:
            self.obj.add_tag(handle)
            commit_method(self.obj, trans)

    def remove_tag(self, obj, handle):
        """
        Remove the given tag from the current object."
        """
        commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(_("Remove Tag from %s") % self.obj_type, self.dbstate.db) as trans:
            self.obj.remove_tag(handle)
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

    def add_url(self, obj):
        """
        Add a new url.
        """
        url = Url()
        try:
            EditUrl(self.dbstate, self.uistate, [], "", url, self.added_url)
        except WindowActiveError:
            pass
        
    def added_url(self, url):
        """
        Save the new url to finish adding it.
        """
        if url:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Url to %s") % self.obj_type, self.dbstate.db) as trans:
                self.obj.add_url(url)
                commit_method(self.obj, trans)

    def edit_url(self, obj, url):
        """
        Edit a url.
        """
        if url:
            try:
                EditUrl(self.dbstate, self.uistate, [], "", url, self.edited_url)
            except WindowActiveError:
                pass

    def edited_url(self, url):
        """
        Save the edited url.
        """
        if url:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Url to %s") % self.obj_type, self.dbstate.db) as trans:
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
                new_list = []
                for url in self.obj.get_url_list():
                    if not url.is_equal(old_url):
                        new_list.append(url)
                commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
                with DbTxn(_("Delete Url from %s") % self.obj_type, self.dbstate.db) as trans:
                    self.obj.set_url_list(new_list)
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
        self.router(None, None, self.obj.get_handle(), "copy-clipboard", self.obj_type)

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
        commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(
            _("Change Privacy for %s") % self.obj_type, self.dbstate.db
        ) as trans:
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
        ref = EventRef()
        ref.set_role(EventRoleType(EventRoleType.FAMILY))
        if self.obj_type == "Family":
            ref.ref = self.obj.handle
        else:
            ref.ref = self.family_backlink

        try:
            EditEventRef(
                self.dbstate, self.uistate, [], event, ref, self.added_new_family_event
            )
        except WindowActiveError:
            pass

    def added_new_family_event(self, reference, primary):
        """
        Finish adding a new event for a family.
        """
        if self.obj_type == "Family":
            family = self.obj
        else:
            family = self.dbstate.db.get_family_from_handle(self.family_backlink)

        with DbTxn(_("Add family event"), self.dbstate.db) as trans:
            family.add_event_ref(reference)
            self.dbstate.db.commit_family(family, trans)

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
            family = self.dbstate.db.get_family_from_handle(handle)
        callback = lambda x: self.added_child(x, handle)
        person = Person()
        name = Name()
        # the editor requires a surname
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father = self.dbstate.db.get_person_from_handle(family.get_father_handle())
        if father:
            preset_name(father, name)
        else:
            mother = self.dbstate.db.get_person_from_handle(family.get_mother_handle())
            if mother:
                preset_name(mother, name)
        person.set_primary_name(name)
        try:
            EditPerson(self.dbstate, self.uistate, [], person, callback=callback)
        except WindowActiveError:
            pass

    def added_child(self, person, family_handle):
        """
        Finish adding the child to the family.
        """
        ref = ChildRef()
        ref.ref = person.get_handle()
        family = self.dbstate.db.get_family_from_handle(family_handle)
        family.add_child_ref(ref)

        with DbTxn(_("Add Child to Family"), self.dbstate.db) as trans:
            # add parentref to child
            person.add_parent_family_handle(family_handle)
            # default relationship is used
            self.dbstate.db.commit_person(person, trans)
            # add child to family
            self.dbstate.db.commit_family(family, trans)

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
        SelectPerson = SelectorFactory("Person")
        if self.obj_type == "Family":
            family = self.obj
            handle = self.obj.handle
        else:
            handle = self.family_backlink
            family = self.dbstate.db.get_family_from_handle(handle)
        # it only makes sense to skip those who are already in the family
        skip_list = [family.get_father_handle(), family.get_mother_handle()]
        skip_list.extend(x.ref for x in family.get_child_ref_list())

        selector = SelectPerson(
            self.dbstate, self.uistate, [], _("Select Child"), skip=skip_list
        )
        person = selector.run()
        if person:
            self.added_child(person, handle)

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.option("layout", "border-width")
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

    
# ------------------------------------------------------------------------
#
# ImageFrame class
#
# ------------------------------------------------------------------------
class ImageFrame(Gtk.Frame):
    """
    A simple class for managing display of an image intended for embedding
    in a GrampsFrame object.
    """

    def __init__(self, dbstate, uistate, obj, size=0):
        Gtk.Frame.__init__(self, expand=False, shadow_type=Gtk.ShadowType.NONE)
        self.dbstate = dbstate
        self.uistate = uistate
        media = obj.get_media_list()
        if media:
            thumbnail = self.get_thumbnail(media[0], size)
            if thumbnail:
                self.add(thumbnail)

    def get_thumbnail(self, media_ref, size):
        """
        Get the thumbnail image.
        """
        mobj = self.dbstate.db.get_media_from_handle(media_ref.ref)
        if mobj and mobj.get_mime_type()[0:5] == "image":
            pixbuf = get_thumbnail_image(
                media_path_full(self.dbstate.db, mobj.get_path()),
                rectangle=media_ref.get_rectangle(),
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
        photo_path = media_path_full(self.dbstate.db, photo.get_path())
        open_file_with_default_application(photo_path, self.uistate)
