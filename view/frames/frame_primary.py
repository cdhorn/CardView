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
import time

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import (
    Attribute,
    ChildRef,
    Event,
    EventRef,
    EventRoleType,
    EventType,
    MediaRef,
    Name,
    Person,
    SrcAttribute,
    Surname,
    Tag,
    Url,
)
from gramps.gen.utils.db import preset_name
from gramps.gui.ddtargets import DdTargets
from gramps.gui.display import display_url
from gramps.gui.editors import (
    EditAttribute,
    EditChildRef,
    EditEventRef,
    EditMediaRef,
    EditPerson,
    EditSrcAttribute,
    EditUrl,
)
from gramps.gui.selectors import SelectorFactory
from gramps.gui.views.tags import EditTag, OrganizeTagsDialog

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext
from ..common.common_utils import (
    attribute_option_text,
    get_bookmarks,
    menu_item,
    submenu_item,
)
from .frame_base import GrampsFrame
from .frame_selectors import get_attribute_types
from .frame_widgets import GrampsImage

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

    def __init__(self, grstate, groptions, primary_obj, reference_tuple=None):
        GrampsFrame.__init__(
            self,
            grstate,
            groptions,
            primary_obj,
            reference_tuple=reference_tuple,
        )
        self.build_layout()
        self.load_layout()

    def load_layout(self):
        """
        Load standard portions of layout.
        """
        if (
            "spouse" in self.groptions.option_space
            or "parent" in self.groptions.option_space
        ):
            if "active" in self.groptions.option_space:
                image_mode = self.get_option("options.group.family.image-mode")
            else:
                image_mode = self.get_option("options.group.family.image-mode")
        else:
            image_mode = self.get_option("image-mode")
        if image_mode and "media" not in self.groptions.option_space:
            self.load_image(image_mode)
        self.widgets["id"].load(self.primary.obj, self.primary.obj_type)
        self.load_attributes()
        self.widgets["icons"].load(self.primary.obj, self.primary.obj_type)

    def load_image(self, image_mode, media_ref=None, crop=True):
        """
        Load primary image for the object if found.
        """
        size = int(image_mode in [2, 4])
        active = "active" in self.groptions.option_space
        image = GrampsImage(
            self.grstate, self.primary.obj, media_ref=media_ref, active=active
        )
        image.load(size, crop)
        self.widgets["image"].add(image)
        if "image" in self.groptions.size_groups:
            self.groptions.size_groups["image"].add_widget(image)

    def add_fact(self, fact, label=None, extra=False):
        """
        Add a fact.
        """
        if extra:
            self.widgets["extra"].add_fact(fact, label=label)
        else:
            self.widgets["facts"].add_fact(fact, label=label)

    def add_event(self, event, extra=False, reference=None, show_age=False):
        """
        Add an event.
        """
        if extra:
            self.widgets["extra"].add_event(
                event, reference=reference, show_age=show_age
            )
        else:
            self.widgets["facts"].add_event(
                event, reference=reference, show_age=show_age
            )

    def load_attributes(self):
        """
        Load any user defined attributes.
        """

        def add_attribute(attribute):
            """
            Check and add attribute if applicable.
            """
            if attribute.get_value():
                value = self.make_label(attribute.get_value(), left=False)
                if label:
                    key = self.make_label(
                        str(attribute.get_type()), left=False
                    )
                else:
                    key = None
                self.widgets["attributes"].add_fact(value, label=key)

        label = self.get_option("attributes-field-show-labels")
        for number in range(1, 9):
            option = self.get_option(
                "".join(("attributes-field-", str(number))),
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
                        add_attribute(attribute)
                        break

    def _primary_drop_handler(self, dnd_type, obj_or_handle, data):
        """
        Handle drop processing largely common to all primary objects.
        """
        if DdTargets.MEDIAOBJ.drag_type == dnd_type:
            self.add_new_media_ref(obj_or_handle)
        elif DdTargets.ATTRIBUTE.drag_type == dnd_type:
            self.added_attribute(obj_or_handle)
        elif DdTargets.URL.drag_type == dnd_type:
            self.added_url(obj_or_handle)
        else:
            self._base_drop_handler(dnd_type, obj_or_handle, data)

    def build_action_menu(self, _dummy_obj, event):
        """
        Build the action menu for a right click. First action will always be
        edit, then any custom actions of the derived children, then the global
        actions supported for all objects enabled for them.
        """
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            action_menu = Gtk.Menu()
            action_menu.append(self._edit_object_option())
            self.add_custom_actions(action_menu)
            if hasattr(self.primary.obj, "attribute_list"):
                action_menu.append(
                    self._attributes_option(
                        self.primary.obj,
                        self.add_attribute,
                        self.remove_attribute,
                        self.edit_attribute,
                    )
                )
            if hasattr(self.primary.obj, "citation_list"):
                action_menu.append(
                    self._citations_option(
                        self.primary.obj,
                        self.add_new_source_citation,
                        self.add_existing_source_citation,
                        self.add_existing_citation,
                        self.remove_citation,
                    )
                )
            if hasattr(self.primary.obj, "media_list"):
                action_menu.append(self._media_option())
            if hasattr(self.primary.obj, "note_list"):
                action_menu.append(
                    self._notes_option(
                        self.primary.obj,
                        self.add_new_note,
                        self.add_existing_note,
                        self.remove_note,
                    )
                )
            if hasattr(self.primary.obj, "tag_list"):
                action_menu.append(self._tags_option())
            if hasattr(self.primary.obj, "urls"):
                action_menu.append(self._urls_option())
            action_menu.append(self._copy_to_clipboard_option())
            if self.grstate.config.get("options.global.enable-bookmarks"):
                action_menu.append(self._bookmark_option())
            action_menu.append(self._change_privacy_option())
            action_menu.add(Gtk.SeparatorMenuItem())
            if self.primary.obj.change:
                text = " ".join(
                    (
                        _("Last changed"),
                        time.strftime(
                            "%x %X", time.localtime(self.primary.obj.change)
                        ),
                    )
                )
            else:
                text = _("Never changed")
            label = Gtk.MenuItem(label=text)
            label.set_sensitive(False)
            action_menu.append(label)

            action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                action_menu.popup_at_pointer(event)
            else:
                action_menu.popup(
                    None, None, None, None, event.button, event.time
                )

    def add_custom_actions(self, action_menu):
        """
        For derived objects to inject their own actions into the menu.
        """

    def goto_person(self, _dummy_obj, handle):
        """
        Change active person for the view.
        """
        person = self.grstate.fetch("Person", handle)
        context = GrampsContext(person, None, None)
        self.grstate.load_page(context.pickled)

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
            message = self._commit_message(
                _("Attribute"), str(attribute.get_type())
            )
            self.primary.obj.add_attribute(attribute)
            self.primary.commit(self.grstate, message)

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
        if self.confirm_action(_("Warning"), prefix, "\n\n<b>", text, "</b>"):
            message = self._commit_message(
                _("Attribute"), str(attribute.get_type()), action="remove"
            )
            self.primary.obj.remove_attribute(attribute)
            self.primary.commit(self.grstate, message)

    def _tags_option(self):
        """
        Build the tags submenu.
        """
        menu = Gtk.Menu()
        tag_add_list = []
        tag_remove_list = []
        for handle in self.grstate.dbstate.db.get_tag_handles():
            tag = self.fetch("Tag", handle)
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
        tag = self.grstate.fetch("Tag", handle)
        message = self._commit_message(_("Tag"), tag.get_name())
        self.primary.obj.add_tag(handle)
        self.primary.commit(self.grstate, message)

    def remove_tag(self, _dummy_obj, handle):
        """
        Remove the given tag from the current object.
        """
        if not handle:
            return
        tag = self.grstate.fetch("Tag", handle)
        message = self._commit_message(
            _("Tag"), tag.get_name(), action="remove"
        )
        if self.primary.obj.remove_tag(handle):
            self.primary.commit(self.grstate, message)

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
        message = self._commit_message(_("Url"), url.get_path())
        self.primary.obj.add_url(url)
        self.primary.commit(self.grstate, message)

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
        message = self._commit_message(
            _("Url"), url.get_path(), action="update"
        )
        self.primary.commit(self.grstate, message)

    def remove_url(self, _dummy_obj, url):
        """
        Remove the given url from the current object.
        """
        if not url:
            return
        text = url.get_path()
        if url.get_description():
            text = "".join((url.get_description(), "\n", text))
        prefix = _(
            "You are about to remove the following url from this object:"
        )
        if self.confirm_action(_("Warning"), prefix, "\n\n<b>", text, "</b>"):
            message = self._commit_message(
                _("Url"), url.get_path(), action="remove"
            )
            if self.primary.obj.remove_url(url):
                self.primary.commit(self.grstate, message)

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
        self.grstate.copy_to_clipboard(
            self.primary.obj_type, self.primary.obj.get_handle()
        )

    def _add_new_family_event_option(self):
        """
        Build menu option for adding a new event for a family.
        """
        if self.primary.obj_type == "Family" or self.groptions.backlink:
            return menu_item(
                "gramps-event",
                _("Add a new family event"),
                self.add_new_family_event,
            )
        return None

    def add_new_family_event(self, _dummy_obj, event_handle=None):
        """
        Add a new event for a family.
        """
        event_ref = EventRef()
        if event_handle:
            for event_ref in self.primary.obj.get_event_ref_list():
                if event_ref.ref == event_handle:
                    return
            event = self.fetch("Event", event_handle)
            event_ref.ref = event_handle
        else:
            event = Event()
            event.set_type(EventType(EventType.MARRIAGE))
        event_ref.set_role(EventRoleType(EventRoleType.FAMILY))
        if self.primary.obj_type == "Family":
            event_ref.ref = self.primary.obj.handle
        else:
            event_ref.ref = self.groptions.backlink
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

    def added_new_family_event(self, event_ref, event):
        """
        Finish adding a new event for a family.
        """
        if self.primary.obj_type == "Family":
            family = self.primary.obj
        else:
            family = self.fetch("Family", self.groptions.backlink)
        message = " ".join(
            (
                _("Added"),
                _("Family"),
                family.get_gramps_id(),
                _("to"),
                _("Event"),
                event.get_gramps_id(),
            )
        )
        with DbTxn(message, self.grstate.dbstate.db) as trans:
            self.grstate.dbstate.db.commit_event(event, trans)
            family.add_event_ref(event_ref)
            self.grstate.dbstate.db.commit_family(family, trans)

    def _add_new_child_option(self):
        """
        Build menu item for adding a new child to the family.
        """
        if self.primary.obj_type == "Family" or self.groptions.backlink:
            return menu_item(
                "gramps-person",
                _("Add a new child to the family"),
                self.add_new_child,
            )
        return None

    def add_new_child(self, *_dummy_obj):
        """
        Add a new child to a family. First create the person.
        """
        if self.primary.obj_type == "Family":
            handle = self.primary.obj.get_handle()
            family = self.primary.obj
        else:
            handle = self.groptions.backlink
            family = self.fetch("Family", handle)
        callback = lambda x: self.adding_child_to_family(x, handle)
        child = Person()
        name = Name()
        name.add_surname(Surname())
        name.set_primary_surname(0)
        father = self.fetch("Person", family.get_father_handle())
        if father:
            preset_name(father, name)
        else:
            mother = self.fetch("Person", family.get_mother_handle())
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
                callback,
            )
        except WindowActiveError:
            pass

    def added_child(self, child_ref, child, family_handle):
        """
        Finish adding the child to the family.
        """
        family = self.fetch("Family", family_handle)
        message = " ".join(
            (
                _("Added"),
                _("Child"),
                child.get_gramps_id(),
                _("to"),
                _("Family"),
                family.get_gramps_id(),
            )
        )
        with DbTxn(message, self.grstate.dbstate.db) as trans:
            family.add_child_ref(child_ref)
            self.grstate.dbstate.db.commit_family(family, trans)
            child.add_parent_family_handle(family_handle)
            self.grstate.dbstate.db.commit_person(child, trans)

    def _add_existing_child_option(self):
        """
        Build menu item for adding existing child to the family.
        """
        if self.primary.obj_type == "Family" or self.groptions.backlink:
            return menu_item(
                "gramps-person",
                _("Add an existing child to the family"),
                self.add_existing_child,
            )
        return None

    def add_existing_child(self, *_dummy_obj):
        """
        Add the child to the family. First select the person.
        """
        select_person = SelectorFactory("Person")
        if self.primary.obj_type == "Family":
            family_handle = self.primary.obj.get_handle()
            family = self.primary.obj
        else:
            family_handle = self.groptions.backlink
            family = self.fetch("Family", family_handle)
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
        for bookmark in get_bookmarks(
            self.grstate.dbstate.db, self.primary.obj_type
        ).get():
            if bookmark == self.primary.obj.get_handle():
                return menu_item(
                    "gramps-bookmark-delete",
                    _("Unbookmark"),
                    self.change_bookmark,
                    False,
                )
        return menu_item(
            "gramps-bookmark", _("Bookmark"), self.change_bookmark, True
        )

    def change_bookmark(self, _dummy_obj, mode):
        """
        Either bookmark or unbookmark the current object.
        """
        bookmarks = get_bookmarks(
            self.grstate.dbstate.db, self.primary.obj_type
        )
        bookmark_list = bookmarks.get()
        if mode:
            if self.primary.obj.get_handle() not in bookmark_list:
                bookmarks.insert(0, self.primary.obj.get_handle())
        else:
            if self.primary.obj.get_handle() in bookmark_list:
                bookmarks.remove(self.primary.obj.get_handle())
        self.widgets["id"].reload(self.primary.obj, self.primary.obj_type)

    def _media_option(self):
        """
        Build the media submenu.
        """
        menu = Gtk.Menu()
        menu.add(
            menu_item(
                "list-add", _("Add a new media item"), self.add_new_media
            )
        )
        menu.add(
            menu_item(
                "list-add",
                _("Add an existing media item"),
                self.add_existing_media,
            )
        )
        if len(self.primary.obj.get_media_list()) > 0:
            removemenu = Gtk.Menu()
            menu.add(
                submenu_item(
                    "gramps-media", _("Remove a media item"), removemenu
                )
            )
            menu.add(Gtk.SeparatorMenuItem())
            menu.add(Gtk.SeparatorMenuItem())
            for media_ref in self.primary.obj.get_media_list():
                media = self.fetch("Media", media_ref.ref)
                text = media.get_description()
                removemenu.add(
                    menu_item(
                        "list-remove", text, self.remove_media_ref, media
                    )
                )
                menu.add(
                    menu_item("gramps-media", text, self.edit_media_ref, media)
                )
        return submenu_item("gramps-media", _("Media"), menu)

    def add_existing_media(self, _dummy_obj):
        """
        Add an existing media item.
        """
        select_media = SelectorFactory("Media")
        selector = select_media(self.grstate.dbstate, self.grstate.uistate, [])
        selection = selector.run()
        if selection:
            self.add_new_media_ref(selection.handle)

    def remove_media_ref(self, _dummy_obj, media):
        """
        Remove a media reference.
        """
        if not media:
            return
        text = media.get_description()
        prefix = _(
            "You are about to remove the following media from this object:"
        )
        extra = _("This removes the reference but does not delete the media.")
        if self.confirm_action(
            _("Warning"), prefix, "\n\n<b>", text, "</b>\n\n", extra
        ):
            message = " ".join(
                (
                    _("Removed"),
                    _("MediaRef"),
                    media.get_gramps_id(),
                    _("from"),
                    self.primary.obj_lang,
                    self.primary.obj.get_gramps_id(),
                )
            )
            self.primary.obj.remove_media_references([media.get_handle()])
            self.primary.commit(self.grstate, message)

    def edit_media_ref(self, _dummy_obj, media):
        """
        Edit a media reference.
        """
        for media_ref in self.primary.obj.get_media_list():
            if media_ref.ref == media.get_handle():
                break
        try:
            EditMediaRef(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                media,
                media_ref,
                self._edited_media_ref,
            )
        except WindowActiveError:
            pass

    def _edited_media_ref(self, media_ref, media):
        """
        Save the edited media reference.
        """
        if not media_ref and media:
            return
        message = self._commit_message(
            _("MediaRef"), media.get_gramps_id(), action="update"
        )
        self.primary.commit(self.grstate, message)

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
        tag = self.grstate.fetch("Tag", handle)
        message = self._commit_message(_("Tag"), tag.get_name())
        self.primary.obj.add_tag(handle)
        self.primary.commit(self.grstate, message)

    def remove_tag(self, _dummy_obj, handle):
        """
        Remove the given tag from the current object.
        """
        if not handle:
            return
        tag = self.grstate.fetch("Tag", handle)
        message = self._commit_message(
            _("Tag"), tag.get_name(), action="remove"
        )
        if self.primary.obj.remove_tag(handle):
            self.primary.commit(self.grstate, message)
