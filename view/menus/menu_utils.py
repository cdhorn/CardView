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
Menu utility functions
"""

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
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.db import family_name

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..actions import action_handler
from ..common.common_utils import citation_option_text
from ..zotero.zotero import GrampsZotero

_ = glocale.translation.sgettext


def menu_item(icon, label, callback, *args):
    """
    Helper for constructing a menu item.
    """
    image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
    item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
    item.connect("activate", callback, *args)
    return item


def submenu_item(icon, label, menu):
    """
    Helper for constructing a submenu item.
    """
    image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU)
    item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=label)
    item.set_submenu(menu)
    return item


def new_menu(icon, label, callback, *args):
    """
    Create and return a new menu with an initial entry.
    """
    menu = Gtk.Menu()
    menu.add(menu_item(icon, label, callback, *args))
    return menu


def new_submenu(menu, icon, label):
    """
    Add and return a newly created submenu.
    """
    submenu = Gtk.Menu()
    menu.add(submenu_item(icon, label, submenu))
    return submenu


def show_menu(menu, widget, event):
    """
    Show the menu.
    """
    menu.attach_to_widget(widget, None)
    menu.show_all()
    if Gtk.get_minor_version() >= 22:
        menu.popup_at_pointer(event)
    else:
        menu.popup(None, None, None, None, event.button, event.time)
    return True


def add_double_separator(menu):
    """
    Add two separator items to menu.
    """
    menu.add(Gtk.SeparatorMenuItem())
    menu.add(Gtk.SeparatorMenuItem())


def add_edit_menu_option(grstate, parent_menu, grobject, grchild=None):
    """
    Build and add the edit menu option.
    """
    target_object = grchild or grobject
    if grchild:
        action = action_handler(grchild.obj_type, grstate, grchild, grobject)
    else:
        action = action_handler(grobject.obj_type, grstate, grobject)
    text = " ".join((_("Edit"), target_object.obj_lang.lower()))
    parent_menu.append(
        menu_item(
            "gtk-edit",
            text,
            action.edit_object,
        )
    )


def add_delete_menu_option(grstate, parent_menu, grobject, grchild=None):
    """
    Build and add the delete menu option.
    """
    if not grobject.is_primary:
        return
    if grchild and grchild.obj_type not in [
        "Attribute",
        "LdsOrd",
        "Name",
        "Url",
    ]:
        return
    target_object = grchild or grobject
    if grchild:
        action = action_handler(grchild.obj_type, grstate, grchild, grobject)
    else:
        action = action_handler(grobject.obj_type, grstate, grobject)
    text = _("Delete %s") % target_object.obj_lang.lower()
    parent_menu.append(
        menu_item(
            "list-remove",
            text,
            action.delete_object,
        )
    )


def add_attributes_menu(grstate, parent_menu, grobject, grchild=None):
    """
    Build and add the attributes submenu.
    """
    if not grstate.config.get("menu.attributes"):
        return
    target_object = grchild or grobject
    if not target_object.has_attributes:
        return
    action = action_handler("Attribute", grstate, None, grobject, grchild)
    menu = new_menu("list-add", _("Add a new attribute"), action.add_attribute)
    attribute_list = target_object.obj.get_attribute_list()
    if attribute_list:
        deletemenu = new_submenu(
            menu, "gramps-attribute", _("Delete an attribute")
        )
        add_double_separator(menu)
        work_list = []
        for attribute in attribute_list:
            text = ": ".join(
                (str(attribute.get_type()), attribute.get_value())
            )
            if len(text) > 50:
                text = "".join((text[:50], "..."))
            work_list.append((text, attribute))
        work_list.sort(key=lambda x: x[0])
        for text, attribute in work_list:
            action = action_handler(
                "Attribute", grstate, attribute, grobject, grchild
            )
            deletemenu.add(
                menu_item("list-remove", text, action.delete_object)
            )
            menu.add(
                menu_item(
                    "gtk-edit",
                    text,
                    action.edit_attribute,
                )
            )
    parent_menu.append(submenu_item("gramps-attribute", _("Attributes"), menu))


def add_citations_menu(grstate, parent_menu, grobject, grchild=None):
    """
    Build and add the citations submenu.
    """
    if not grstate.config.get("menu.citations"):
        return
    target_object = grchild or grobject
    if not target_object.has_citations:
        return
    db = grstate.dbstate.db
    delete_enabled = grstate.config.get("menu.delete-submenus")
    action = action_handler("Citation", grstate, None, grobject, grchild)
    menu = new_menu(
        "list-add",
        _("Add new citation for a new source"),
        action.add_new_source_citation,
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add new citation for an existing source"),
            action.add_existing_source_citation,
        )
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add an existing citation"),
            action.add_existing_citation,
        )
    )
    if grstate.config.get("general.zotero-enabled"):
        zotero = GrampsZotero(db)
        if zotero.online:
            menu.add(
                menu_item(
                    "list-add",
                    _("Add citation using Zotero"),
                    action.add_zotero_citation,
                )
            )
        else:
            entry = menu_item(
                "list-add",
                _("Add citation using Zotero (currently offline)"),
                action.add_zotero_citation,
            )
            entry.set_sensitive(False)
            menu.add(entry)
    citation_list = target_object.obj.get_citation_list()
    if citation_list:
        removemenu = new_submenu(
            menu, "gramps-citation", _("Remove a citation")
        )
        if delete_enabled:
            deletemenu = new_submenu(
                menu, "gramps-citation", _("Delete a citation")
            )
        add_double_separator(menu)
        work_list = []
        for citation_handle in citation_list:
            citation = db.get_citation_from_handle(citation_handle)
            text = citation_option_text(db, citation)
            work_list.append((text, citation))
        work_list.sort(key=lambda x: x[0])
        for text, citation in work_list:
            action = action_handler(
                "Citation", grstate, citation, grobject, grchild
            )
            removemenu.add(
                menu_item("list-remove", text, action.remove_citation)
            )
            if delete_enabled:
                deletemenu.add(
                    menu_item("list-remove", text, action.delete_object)
                )
            menu.add(menu_item("gtk-edit", text, action.edit_citation))
    parent_menu.append(submenu_item("gramps-citation", _("Citations"), menu))


def add_notes_menu(grstate, parent_menu, grobject, grchild=None):
    """
    Build and add the notes submenu.
    """
    if not grstate.config.get("menu.notes"):
        return
    target_object = grchild or grobject
    if not target_object.has_notes:
        return
    delete_enabled = grstate.config.get("menu.delete-submenus")
    action = action_handler("Note", grstate, None, grobject, grchild)
    menu = new_menu("list-add", _("Add a new note"), action.add_new_note)
    menu.add(
        menu_item(
            "list-add", _("Add an existing note"), action.add_existing_note
        )
    )
    note_list = target_object.obj.get_note_list()
    if note_list:
        removemenu = new_submenu(menu, "gramps-notes", _("Remove a note"))
        if delete_enabled:
            deletemenu = new_submenu(menu, "gramps-notes", _("Delete a note"))
        add_double_separator(menu)
        note_list = get_sorted_notes(grstate.dbstate.db, note_list)
        for text, note in note_list:
            action = action_handler("Note", grstate, note, grobject, grchild)
            removemenu.add(menu_item("list-remove", text, action.remove_note))
            if delete_enabled:
                deletemenu.add(
                    menu_item("list-remove", text, action.delete_object)
                )
            menu.add(menu_item("gtk-edit", text, action.edit_note))
    if grstate.config.get("menu.notes-children") and not grchild:
        get_child_notes(menu, grstate, grobject, grchild)
    parent_menu.append(submenu_item("gramps-notes", _("Notes"), menu))


def get_child_notes(menu, grstate, grobject, grchild):
    """
    Find and add child notes to menu.
    """
    handle_list = []
    for child_obj in grobject.obj.get_note_child_list():
        for note_handle in child_obj.get_note_list():
            if note_handle not in handle_list:
                handle_list.append(note_handle)
    note_list = get_sorted_notes(grstate.dbstate.db, handle_list)
    if note_list:
        add_double_separator(menu)
        for text, note in note_list:
            action = action_handler("Note", grstate, note, grobject, grchild)
            menu.add(menu_item("gtk-edit", text, action.edit_note))


def get_sorted_notes(db, handle_list):
    """
    Return a sorted note list.
    """
    note_list = []
    for note_handle in handle_list:
        note = db.get_note_from_handle(note_handle)
        notetype = str(note.get_type())
        text = note.get()[:40].replace("\n", " ")
        if len(text) > 39:
            text = "".join((text, "..."))
        text = ": ".join((notetype, text))
        note_list.append((text, note))
    note_list.sort(key=lambda x: x[0])
    return note_list


def add_privacy_menu_option(grstate, parent_menu, grobject, grchild=None):
    """
    Build and add the privacy menu entry.
    """
    if not grstate.config.get("menu.privacy"):
        return
    action = action_handler("Privacy", grstate, grobject, grchild)
    if not action.is_valid():
        return
    if action.is_set():
        parent_menu.append(
            menu_item("gramps-unlock", _("Make public"), action.toggle, False)
        )
    else:
        parent_menu.append(
            menu_item("gramps-lock", _("Make private"), action.toggle, True)
        )


def add_clipboard_menu_option(grstate, parent_menu, callback):
    """
    Build and add the copy to clipboard menu entry.
    """
    if not grstate.config.get("menu.clipboard"):
        return
    parent_menu.append(
        menu_item("edit-copy", _("Copy to clipboard"), callback)
    )


def add_bookmark_menu_option(grstate, parent_menu, grobject):
    """
    Build and add the bookmark menu entry.
    """
    if not grstate.config.get("menu.bookmarks"):
        return
    action = action_handler("Bookmark", grstate, grobject)
    if action.is_set():
        parent_menu.append(
            menu_item(
                "gramps-bookmark-delete", _("Unbookmark"), action.toggle, False
            )
        )
    else:
        parent_menu.append(
            menu_item("gramps-bookmark", _("Bookmark"), action.toggle, True)
        )


def add_tags_menu(grstate, parent_menu, grobject, sort_by_name=False):
    """
    Build and add the tags submenu.
    """
    if not grstate.config.get("menu.tags"):
        return
    if not grobject.has_tags:
        return
    delete_enabled = grstate.config.get("menu.delete-submenus")
    menu = Gtk.Menu()
    tag_list = grobject.obj.get_tag_list()
    tag_add_list = []
    tag_remove_list = []
    tag_delete_list = []
    db = grstate.dbstate.db
    for tag_handle in db.get_tag_handles():
        tag = db.get_tag_from_handle(tag_handle)
        if tag_handle in tag_list:
            tag_remove_list.append(tag)
        else:
            tag_add_list.append(tag)
        tag_delete_list.append(tag)
    for list_item in [tag_add_list, tag_remove_list, tag_delete_list]:
        if sort_by_name:
            list_item.sort(key=lambda x: x.name)
        else:
            list_item.sort(key=lambda x: x.priority)
    prepare_tag_menu_item(grstate, menu, grobject, tag_add_list, "list-add")
    prepare_tag_menu_item(
        grstate, menu, grobject, tag_remove_list, "list-remove"
    )
    if delete_enabled:
        prepare_tag_menu_item(
            grstate, menu, grobject, tag_delete_list, "list-delete"
        )
    action = action_handler("Tag", grstate, None, grobject)
    menu.add(menu_item("gramps-tag", _("Create new tag"), action.new_tag))
    menu.add(menu_item("gramps-tag", _("Organize tags"), action.organize_tags))
    parent_menu.append(submenu_item("gramps-tag", _("Tags"), menu))


def prepare_tag_menu_item(grstate, parent_menu, grobject, tag_list, icon_name):
    """
    Prepare menu options for a tag action.
    """
    if tag_list:
        if icon_name == "list-add":
            label = _("Add a tag")
        elif icon_name == "list-remove":
            label = _("Remove a tag")
        else:
            label = _("Delete a tag")
        menu = Gtk.Menu()
        for tag in tag_list:
            action = action_handler("Tag", grstate, tag, grobject)
            if icon_name == "list-add":
                menu.add(menu_item(icon_name, tag.name, action.add_tag))
            elif icon_name == "list-remove":
                menu.add(menu_item(icon_name, tag.name, action.remove_tag))
            else:
                menu.add(
                    menu_item("list-remove", tag.name, action.delete_object)
                )
        parent_menu.append(submenu_item("gramps-tag", label, menu))


def add_urls_menu(grstate, parent_menu, grobject):
    """
    Build and add the urls submenu.
    """
    if not grstate.config.get("menu.urls"):
        return
    if not grobject.has_urls:
        return
    action = action_handler("Url", grstate, None, grobject)
    menu = new_menu("list-add", _("Add a url"), action.add_url)
    url_list = grobject.obj.get_url_list()
    if url_list:
        editmenu = new_submenu(menu, "gramps-url", _("Edit a url"))
        deletemenu = new_submenu(menu, "gramps-url", _("Delete a url"))
        add_double_separator(menu)
        url_sort_list = []
        for url in grobject.obj.get_url_list():
            text = url.get_description()
            if not text:
                text = url.get_path()
            url_sort_list.append((text, url))
        url_sort_list.sort(key=lambda x: x[0])
        for text, url in url_sort_list:
            action = action_handler("Url", grstate, url, grobject)
            editmenu.add(menu_item("gtk-edit", text, action.edit_url))
            deletemenu.add(
                menu_item("list-remove", text, action.delete_object)
            )
            menu.add(menu_item("gramps-url", text, action.launch_url))
    parent_menu.append(submenu_item("gramps-url", _("Urls"), menu))


def add_media_menu(grstate, parent_menu, grobject):
    """
    Build and add the media submenu.
    """
    if not grstate.config.get("menu.media"):
        return
    if not grobject.has_media:
        return
    delete_enabled = grstate.config.get("menu.delete-submenus")
    action = action_handler("Media", grstate, None, grobject)
    menu = new_menu(
        "list-add", _("Add a new media item"), action.add_new_media
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add an existing media item"),
            action.add_existing_media,
        )
    )
    media_list = grobject.obj.get_media_list()
    if media_list:
        removemenu = new_submenu(
            menu, "gramps-media", _("Remove a media item")
        )
        if delete_enabled:
            deletemenu = new_submenu(
                menu, "gramps-media", _("Delete a media item")
            )
        add_double_separator(menu)
        for media_ref in media_list:
            action = action_handler("Media", grstate, media_ref, grobject)
            media = grstate.dbstate.db.get_media_from_handle(media_ref.ref)
            text = media.get_description()
            removemenu.add(
                menu_item("list-remove", text, action.remove_media_reference)
            )
            if delete_enabled:
                deletemenu.add(
                    menu_item("list-remove", text, action.delete_object)
                )
            menu.add(menu_item("gtk-edit", text, action.edit_media))
    parent_menu.append(submenu_item("gramps-media", _("Media"), menu))


def add_names_menu(grstate, parent_menu, grobject):
    """
    Build and add the names submenu.
    """
    if not grstate.config.get("menu.names"):
        return
    action = action_handler("Name", grstate, None, grobject)
    menu = new_menu("list-add", _("Add a new name"), action.add_name)
    name_list = grobject.obj.get_alternate_names()
    if name_list:
        deletemenu = new_submenu(menu, "gramps-person", _("Delete a name"))
        add_double_separator(menu)
        name = grobject.obj.get_primary_name()
        action = action_handler("Name", grstate, name, grobject)
        given_name = name.get_regular_name()
        menu.add(menu_item("gtk-edit", given_name, action.edit_name))
        for name in name_list:
            action = action_handler("Name", grstate, name, grobject)
            given_name = name.get_regular_name()
            deletemenu.add(
                menu_item("list-remove", given_name, action.delete_object)
            )
            menu.add(menu_item("gtk-edit", given_name, action.edit_name))
    parent_menu.append(submenu_item("gramps-person", _("Names"), menu))


def add_associations_menu(grstate, parent_menu, grobject):
    """
    Build and add the associations submenu.
    """
    if not grstate.config.get("menu.associations"):
        return
    db = grstate.dbstate.db
    action = action_handler("Person", grstate, grobject)
    menu = new_menu(
        "list-add",
        _("Add an association for a new person"),
        action.add_new_person_reference,
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add an association for an existing person"),
            action.add_existing_person_reference,
        )
    )
    person_ref_list = grobject.obj.get_person_ref_list()
    if person_ref_list:
        removemenu = new_submenu(
            menu, "gramps-person", _("Delete an association")
        )
        add_double_separator(menu)
        for person_ref in person_ref_list:
            person = db.get_person_from_handle(person_ref.ref)
            person_name = name_displayer.display(person)
            action = action_handler("Person", grstate, grobject, person_ref)
            removemenu.add(
                menu_item(
                    "list-remove",
                    person_name,
                    action.remove_person_reference,
                )
            )
            menu.add(
                menu_item(
                    "gtk-edit",
                    person_name,
                    action.edit_person_reference,
                )
            )
    parent_menu.append(submenu_item("gramps-person", _("Associations"), menu))


def add_parents_menu(grstate, parent_menu, grobject):
    """
    Build and add the parents submenu.
    """
    if not grstate.config.get("menu.parents"):
        return
    db = grstate.dbstate.db
    action = action_handler("Person", grstate, grobject)
    menu = new_menu(
        "gramps-parents-add",
        _("Add a new set of parents"),
        action.add_new_parents,
    )
    menu.add(
        menu_item(
            "gramps-parents-open",
            _("Add as child to an existing family"),
            action.add_existing_parents,
        )
    )
    parent_family_list = grobject.obj.get_parent_family_handle_list()
    if parent_family_list:
        add_double_separator(menu)
        for family_handle in parent_family_list:
            family = db.get_family_from_handle(family_handle)
            family_text = family_name(family, db)
            action = action_handler("Family", grstate, family)
            menu.add(
                menu_item(
                    "gtk-edit",
                    family_text,
                    action.edit_family,
                )
            )
    parent_menu.append(submenu_item("gramps-parents", _("Parents"), menu))


def add_partners_menu(grstate, parent_menu, grobject):
    """
    Build and add submenu the partners submenu.
    """
    if not grstate.config.get("menu.spouses"):
        return
    db = grstate.dbstate.db
    action = action_handler("Person", grstate, grobject)
    menu = new_menu(
        "gramps-spouse",
        _("Add as parent of new family"),
        action.add_new_family,
    )
    family_list = grobject.obj.get_family_handle_list()
    if family_list:
        add_double_separator(menu)
        for family_handle in family_list:
            family = db.get_family_from_handle(family_handle)
            family_text = family_name(family, db)
            action = action_handler("Family", grstate, family)
            menu.add(
                menu_item(
                    "gtk-edit",
                    family_text,
                    action.edit_family,
                )
            )
    parent_menu.append(submenu_item("gramps-spouse", _("Spouses"), menu))


def add_participants_menu(grstate, parent_menu, grobject, participants):
    """
    Build and add the participants submenu.
    """
    if not grstate.config.get("menu.participants"):
        return
    action = action_handler("Event", grstate, grobject)
    menu = new_menu(
        "gramps-person",
        _("Add a new person as a participant"),
        action.add_new_participant,
    )
    menu.add(
        menu_item(
            "gramps-person",
            _("Add an existing person as a participant"),
            action.add_existing_participant,
        )
    )
    enable_goto = grstate.config.get("menu.go-to-person")
    if len(participants) > 1:
        if enable_goto:
            gotomenu = new_submenu(
                menu, "gramps-person", _("Go to a participant")
            )
        editmenu = new_submenu(menu, "gramps-person", _("Edit a participant"))
        removemenu = new_submenu(
            menu, "gramps-person", _("Remove a participant")
        )
        add_double_separator(menu)
        participant_list = get_sorted_participants(participants)
        for (text, person, dummy_event_ref) in participant_list:
            action = action_handler("Person", grstate, person)
            if enable_goto:
                gotomenu.add(
                    menu_item("gramps-person", text, action.goto_person)
                )
            editmenu.add(
                menu_item(
                    "gtk-edit",
                    text,
                    action.edit_person,
                )
            )
            action = action_handler("Event", grstate, grobject, person)
            removemenu.add(
                menu_item(
                    "list-remove",
                    text,
                    action.remove_participant,
                )
            )
            menu.add(
                menu_item(
                    "gtk-edit",
                    text,
                    action.edit_participant,
                )
            )
        if len(removemenu) == 0:
            removemenu.destroy()
    parent_menu.append(submenu_item("gramps-person", _("Participants"), menu))


def get_sorted_participants(participants):
    """
    Return sorted participants list.
    """
    participant_list = []
    for (obj_type, obj, obj_event_ref, obj_name) in participants:
        if obj_type == "Person":
            text = "".join((str(obj_event_ref.get_role()), ": ", obj_name))
            participant_list.append((text, obj, obj_event_ref))
    participant_list.sort(key=lambda x: x[0])
    return participant_list


def add_repositories_menu(grstate, parent_menu, grobject):
    """
    Build and add the repositories submenu.
    """
    if not grstate.config.get("menu.repositories"):
        return
    db = grstate.dbstate.db
    action = action_handler("Source", grstate, grobject)
    menu = new_menu(
        "list-add",
        _("Add a new repository"),
        action.add_new_repository_reference,
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add an existing repository"),
            action.add_existing_repository,
        )
    )
    reporef_list = grobject.obj.get_reporef_list()
    if reporef_list:
        removemenu = new_submenu(
            menu, "gramps-repository", _("Remove a repository")
        )
        add_double_separator(menu)
        for repo_ref in reporef_list:
            repository = db.get_repository_from_handle(repo_ref.ref)
            repository_name = repository.get_name()
            action = action_handler("Source", grstate, grobject, repo_ref)
            removemenu.add(
                menu_item(
                    "list-remove",
                    repository_name,
                    action.remove_repository_reference,
                )
            )
            menu.add(
                menu_item(
                    "gtk-edit",
                    repository_name,
                    action.edit_repository_reference,
                )
            )
    parent_menu.append(
        submenu_item("gramps-repository", _("Repositories"), menu)
    )


def add_person_menu_options(grstate, parent_menu, grobject, family, context):
    """
    Add context sensitive person menu options.
    """
    action = action_handler("Family", grstate, family, grobject)
    if context in ["parent", "spouse", "family", "sibling", "child"]:
        add_family_event_option(parent_menu, action)
    if context in ["parent", "spouse"]:
        add_family_child_options(parent_menu, action)
        parent_menu.append(
            menu_item(
                "list-remove",
                _("Remove parent from this family"),
                action.remove_partner,
            )
        )
        if has_spouse(family, grobject.obj):
            parent_menu.append(
                menu_item(
                    "list-remove",
                    _("Remove spouse from this family"),
                    action.remove_spouse,
                )
            )
    if context in ["sibling", "child"]:
        if not is_preferred_parents(family, grobject.obj):
            parent_menu.append(
                menu_item(
                    "list-remove",
                    _("Make current parents preferred"),
                    action.set_main_parents,
                )
            )
        parent_menu.append(
            menu_item(
                "list-remove",
                _("Remove child from this family"),
                action.remove_child,
            )
        )


def add_family_event_option(parent_menu, action):
    """
    Add the family event options.
    """
    parent_menu.append(
        menu_item(
            "gramps-event",
            _("Add a new family event"),
            action.add_new_event,
        )
    )


def add_family_child_options(parent_menu, action):
    """
    Add the family child options.
    """
    parent_menu.append(
        menu_item(
            "gramps-person",
            _("Add a new child to the family"),
            action.add_new_child,
        )
    )
    parent_menu.append(
        menu_item(
            "gramps-person",
            _("Add an existing child to the family"),
            action.add_existing_child,
        )
    )


def is_preferred_parents(family, person):
    """
    Return true if family the preferred one.
    """
    main_parents = person.get_main_parents_family_handle()
    return family.get_handle() == main_parents


def has_spouse(family, parent):
    """
    Return true if parent has a spouse.
    """
    father_handle = family.get_father_handle()
    if father_handle and father_handle != parent.get_handle():
        return True
    mother_handle = family.get_mother_handle()
    if mother_handle and mother_handle != parent.get_handle():
        return True
    return False


def add_ldsords_menu(grstate, parent_menu, grobject):
    """
    Build and add the lds ordinances submenu.
    """
    if not grstate.config.get("menu.ordinances"):
        return
    action = action_handler("LdsOrd", grstate, None, grobject)
    menu = new_menu("list-add", _("Add a new ordinance"), action.add_ordinance)
    ordinance_list = grobject.obj.get_lds_ord_list()
    if ordinance_list:
        deletemenu = new_submenu(
            menu, "gramps-person", _("Delete an ordinance")
        )
        add_double_separator(menu)
        for ordinance in ordinance_list:
            action = action_handler("LdsOrd", grstate, ordinance, grobject)
            ordinance_date = ordinance.get_date_object()
            if ordinance_date:
                date = glocale.date_displayer.display(ordinance_date)
                text = "".join((date, ": ", ordinance.type2str()))
            else:
                text = ordinance.type2str()
            deletemenu.add(
                menu_item("list-remove", text, action.delete_object)
            )
            menu.add(menu_item("gtk-edit", text, action.edit_object))
    parent_menu.append(submenu_item("gramps-person", _("Ordinances"), menu))


def add_enclosed_places_menu(grstate, parent_menu, grobject):
    """
    Build and add the enclosed places submenu.
    """
    if not grstate.config.get("menu.enclosed-places"):
        return
    action = action_handler("Place", grstate, None, grobject)
    menu = new_menu(
        "list-add",
        _("Add a new enclosed place"),
        action.add_new_enclosed_place,
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add an existing enclosed place"),
            action.add_existing_enclosed_place,
        )
    )
    db = grstate.dbstate.db
    place_list = get_enclosed_places(db, grobject.obj)
    if place_list:
        removemenu = new_submenu(
            menu, "gramps-place", _("Remove an enclosed place")
        )
        add_double_separator(menu)
        for place in place_list:
            action = action_handler("Place", grstate, place, grobject)
            text = place_displayer.display(db, place)
            removemenu.add(
                menu_item("list-remove", text, action.remove_place_reference)
            )
            menu.add(menu_item("gtk-edit", text, action.edit_object))
    parent_menu.append(
        submenu_item("gramps-place", _("Enclosed Places"), menu)
    )


def get_enclosed_places(db, place):
    """
    Build list of enclosed places. This only returns the first set of children.
    """
    places = []
    for (dummy_obj_type, obj_handle) in db.find_backlink_handles(
        place.get_handle(), ["Place"]
    ):
        places.append(db.get_place_from_handle(obj_handle))
    return places
