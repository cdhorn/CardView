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
    EditPerson,
    EditFamily,
    EditEvent,
    EditEventRef,
    EditCitation,
    EditPlace,
    EditNote,
    EditAttribute,
    EditSrcAttribute,
    EditUrl
)
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    Attribute,
    SrcAttribute,
    Person,
    ChildRef,
    Family,
    Event,
    EventRef,
    EventType,
    EventRoleType,
    Citation,
    Span,
    Place,
    Source,
    Repository,
    Name,
    Note,
    Surname,
    Tag,
    Url
)
from gramps.gen.utils.db import preset_name
from gramps.gen.utils.file import media_path_full
from gramps.gui.display import display_url
from gramps.gui.selectors import SelectorFactory
from gramps.gui.utils import open_file_with_default_application
from gramps.gen.utils.thumbnails import get_thumbnail_image
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
    "Person": EditPerson,
    "Place": EditPlace,
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
        If enabled confirm a user requested action.
        """
        if not self.config.get(
            "{}.layout.enable-warnings".format(self.space)
        ):
            return True
        dialog = Gtk.Dialog(parent=self.uistate.window)
        dialog.set_title(title)
        dialog.set_default_size(400, 300)
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

    def get_family_text(self, handle):
        family = self.dbstate.db.get_family_from_handle(handle)
        text = ""
        if family.father_handle:
            father = self.dbstate.db.get_person_from_handle(family.father_handle)
            text = name_displayer.display(father)
        if family.mother_handle:
            mother = self.dbstate.db.get_person_from_handle(family.mother_handle)
            name = name_displayer.display(mother)
            if text:
                text = "{} {} {}".format(text, _("and"), name)
            elif name:
                text = name
        return text
        

# ------------------------------------------------------------------------
#
# GrampsFrame class
#
# ------------------------------------------------------------------------
class GrampsFrame(Gtk.VBox, GrampsConfig):
    """
    The GrampsFrame class provides core methods for constructing the view
    for a primary Gramps object.
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

        self.body = Gtk.HBox()
        self.frame = Gtk.Frame(shadow_type=Gtk.ShadowType.NONE)
        if eventbox:
            self.eventbox = Gtk.EventBox()
            self.eventbox.add(self.body)
            self.eventbox.connect("button-press-event", self.route_action)
            self.frame.add(self.eventbox)
        else:
            self.frame.add(self.body)
        self.add(self.frame)

        if isinstance(self.obj, Person):
            self.obj_type = "Person"
        elif isinstance(self.obj, Family):
            self.obj_type = "Family"
        elif isinstance(self.obj, Event):
            self.obj_type = "Event"
        elif isinstance(self.obj, Place):
            self.obj_type = "Place"
        elif isinstance(self.obj, Source):
            self.obj_type = "Source"
        elif isinstance(self.obj, Citation):
            self.obj_type = "Citation"
        elif isinstance(self.obj, Repository):
            self.obj_type = "Repository"
        elif isinstance(self.obj, Note):
            self.obj_type = "Note"

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
        Build the action menu for a right click.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.action_menu = Gtk.Menu()
            self.action_menu.append(self._edit_object_option())
            self.add_custom_actions()
            self.action_menu.append(self._attributes_option())
            self.action_menu.append(self._notes_option())
            item = self._tags_option()
            if item:
                self.action_menu.append(item)
            item = self._urls_option()
            if item:
                self.action_menu.append(item)
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
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
        item.set_submenu(menu)
        return item

    def _edit_object_option(self):
        """
        Construct the edit object menu option.
        """
        if self.obj_type == "Person":
            name = _("Edit %s") % name_displayer.display(self.obj)
        else:
            name = _("Edit {}".format(self.obj_type.lower()))
        return self._menu_item("gtk-edit", name, self.edit_self)

    def edit_self(self, *obj):
        """
        Launch the desired editor based on object type.
        """
        try:
            _EDITORS[self.obj_type](self.dbstate, self.uistate, [], self.obj)
        except WindowActiveError:
            pass

    def edit_object(self, skip, obj, obj_type):
        """
        Launch the desired editor based on object type.
        """
        try:
            _EDITORS[obj_type](self.dbstate, self.uistate, [], obj)
        except WindowActiveError:
            pass        

    def _copy_to_clipboard_option(self):
        """
        Construct menu option to copy current object to clipboard.
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
        Construct the privacy menu option based on the current state.
        """
        if self.obj.private:
            return self._menu_item("gramps-unlock", _("Make public"), self.change_privacy, False)
        return self._menu_item("gramps-lock", _("Make private"), self.change_privacy, True)

    def change_privacy(self, obj, mode):
        """
        Update the privacy indicator.
        """
        commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(
            _("Change Privacy for %s") % self.obj_type, self.dbstate.db
        ) as trans:
            self.obj.set_privacy(mode)
            commit_method(self.obj, trans)

    def _tags_option(self):
        """
        If applicable generate menu option for tag addition with available tags.
        """
        menu = Gtk.Menu()
        menu.add(self._menu_item("gramps-tag", _("Create new tag"), self.new_tag))
        menu.add(self._menu_item("gramps-tag", _("Organize tags"), self.organize_tags))
        tag_list = self.dbstate.db.get_tag_handles()
        if len(tag_list) > 0:
            tag_add_list = []
            tag_remove_list = []
            for handle in tag_list:
                tag = self.dbstate.db.get_tag_from_handle(handle)
                if handle in self.obj.tag_list:
                    tag_remove_list.append(tag)
                else:
                    tag_add_list.append(tag)
            if tag_add_list:
                if self.option("layout", "sort-tags-by-name"):
                    tag_add_list.sort(key = lambda x: x.name)
                else:
                    tag_add_list.sort(key = lambda x: x.priority)
            if tag_remove_list:
                if self.option("layout", "sort-tags-by-name"):
                    tag_remove_list.sort(key = lambda x: x.name)
                else:
                    tag_remove_list.sort(key = lambda x: x.priority)
            separate = False
            if len(tag_list) > 10:
                separate = True
            if tag_add_list and not tag_remove_list:
                separate = False
            if tag_remove_list and not tag_add_list:
                separate = False
            if separate:
                add_menu = Gtk.Menu()
                for tag in tag_add_list:
                    add_menu.add(self._menu_item("list-add", tag.name, self.add_tag, tag.handle))
                menu.add(self._submenu_item("gramps-tag", _("Add tag"), add_menu))
                remove_menu = Gtk.Menu()
                for tag in tag_remove_list:
                    remove_menu.add(self._menu_item("list-remove", tag.name, self.remove_tag, tag.handle))
                menu.add(self._submenu_item("gramps-tag", _("Remove tag"), remove_menu))
            else:
                menu.add(Gtk.SeparatorMenuItem())
                for tag in tag_add_list:
                    menu.add(self._menu_item("list-add", tag.name, self.add_tag, tag.handle))
                for tag in tag_remove_list:
                    menu.add(self._menu_item("list-remove", tag.name, self.remove_tag, tag.handle))
        return self._submenu_item("gramps-tag", _("Tags"), menu)

    def new_tag(self, obj):
        """
        Add a new tag.
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
        Add the requested tag to the active object.
        """
        commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(_("Add Tag to %s") % self.obj_type, self.dbstate.db) as trans:
            self.obj.add_tag(handle)
            commit_method(self.obj, trans)

    def remove_tag(self, obj, handle):
        """
        Remove the requested tag from the active object."
        """
        commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(_("Remove Tag from %s") % self.obj_type, self.dbstate.db) as trans:
            self.obj.remove_tag(handle)
            commit_method(self.obj, trans)

    def _notes_option(self):
        """
        Build note option menu. We support add new under that as well as edit existing.
        """
        if len(self.obj.get_note_list()) > 0:
            menu = Gtk.Menu()
            menu.add(self._menu_item("list-add", _("Add new note"), self.add_note))
            menu.add(Gtk.SeparatorMenuItem())
            for handle in self.obj.get_note_list():
                note = self.dbstate.db.get_note_from_handle(handle)
                text = note.get()[:85].replace('\n', ' ')
                if len(text) > 80:
                    text = text[:80]+"..."
                menu.add(self._menu_item("gramps-notes", text, self.edit_note, note.handle))
            return self._submenu_item("gramps-notes", _("Notes"), menu)
        return self._menu_item("gramps-notes", _("Add new note"), self.add_note)

    def add_note(self, obj):
        """
        Add a new note to the active object.
        """
        note = Note()
        try:
            EditNote(self.dbstate, self.uistate, [], note, self.added_note)
        except WindowActiveError:
            pass
        
    def added_note(self, handle):
        """
        Finish attaching note to the active object."
        """
        if handle:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Note to %s") % self.obj_type, self.dbstate.db) as trans:
                self.obj.add_note(handle)
                commit_method(self.obj, trans)

    def edit_note(self, obj, handle):
        """
        Edit a note for the active object.
        """
        note = self.dbstate.db.get_note_from_handle(handle)
        try:
            EditNote(self.dbstate, self.uistate, [], note)
        except WindowActiveError:
            pass

    def _attributes_option(self):
        """
        Build attributes option menu. We support add new under that as well as edit existing.
        """
        if len(self.obj.get_attribute_list()) > 0:
            menu = Gtk.Menu()
            menu.add(self._menu_item("list-add", _("Add new attribute"), self.add_attribute))
            menu.add(Gtk.SeparatorMenuItem())
            for attribute in self.obj.get_attribute_list():
                text = "{}: {}".format(attribute.get_type(), attribute.get_value())
                if len(text) > 80:
                    text = text[:80]+"..."
                menu.add(self._menu_item("gramps-attribute", text, self.edit_attribute, attribute))
            return self._submenu_item("gramps-attribute", _("Attributes"), menu)
        return self._menu_item("gramps-attribute", _("Add attribute"), self.add_attribute)

    def _get_attribute_types(self):
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
        Add a new attribute to the active object.
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
        Finish attaching attribute to the active object."
        """
        if attribute:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Attribute to %s") % self.obj_type, self.dbstate.db) as trans:
                self.obj.add_attribute(attribute)
                commit_method(self.obj, trans)

    def edit_attribute(self, obj, attribute):
        """
        Edit an attribute for the active object.
        """
        attribute_types = self._get_attribute_types()
        try:
            if self.obj_type in ["Source", "Citation"]:
                EditSrcAttribute(self.dbstate, self.uistate, [], attribute, "", attribute_types, self.added_attribute)                
            else:
                EditAttribute(self.dbstate, self.uistate, [], attribute, "", attribute_types, self.edited_attribute)
        except WindowActiveError:
            pass

    def edited_attribute(self, attribute):
        """
        Save the edited attribute for the active object."
        """
        if attribute:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Updated Attribute for %s") % self.obj_type, self.dbstate.db) as trans:
                commit_method(self.obj, trans)
        
    def _urls_option(self):
        """
        Build urls option menu. We support add new under that and launching existing.
        """
        if not hasattr(self.obj, "urls"):
            return None
        if len(self.obj.get_url_list()) > 0:
            menu = Gtk.Menu()
            menu.add(self._menu_item("list-add", _("Add new url"), self.add_url))
            menu.add(Gtk.SeparatorMenuItem())
            for url in self.obj.get_url_list():
                text = url.get_description()
                if not text:
                    text = url.get_path()
                if text:
                    menu.add(self._menu_item("gramps-url", text, self.launch_url, url))
            return self._submenu_item("gramps-url", _("Urls"), menu)
        return self._menu_item("gramps-url", _("Add url"), self.add_url)

    def add_url(self, obj):
        """
        Add a new url to the active object.
        """
        url = Url()
        try:
            EditUrl(self.dbstate, self.uistate, [], "", url, self.added_url)
        except WindowActiveError:
            pass
        
    def added_url(self, url):
        """
        Finish attaching new url to the active object."
        """
        if url:
            commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
            with DbTxn(_("Add Url to %s") % self.obj_type, self.dbstate.db) as trans:
                self.obj.add_url(url)
                commit_method(self.obj, trans)

    def launch_url(self, obj, url):
        """
        Launch a url.
        """
        if url.get_path():
            display_url(url.get_path())

    def set_css_style(self):
        """
        Apply some simple styling to the frame.
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
