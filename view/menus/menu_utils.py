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
Menu utility functions
"""

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
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.utils.db import family_name

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import citation_option_text, get_bookmarks

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


def add_attributes_menu(parent_menu, grobject, callbacks):
    """
    Build and add the attributes submenu.
    """
    if not grobject.has_attributes:
        return
    (add_attribute, edit_attribute, remove_attribute) = callbacks
    menu = new_menu("list-add", _("Add a new attribute"), add_attribute)
    attribute_list = grobject.obj.get_attribute_list()
    if attribute_list:
        removemenu = new_submenu(
            menu, "gramps-attribute", _("Remove an attribute")
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
            removemenu.add(
                menu_item("list-remove", text, remove_attribute, attribute)
            )
            menu.add(
                menu_item(
                    "gramps-attribute",
                    text,
                    edit_attribute,
                    attribute,
                )
            )
    parent_menu.append(submenu_item("gramps-attribute", _("Attributes"), menu))


def add_citations_menu(parent_menu, db, grobject, callbacks, zotero=False):
    """
    Build and add the citations submenu.
    """
    if not grobject.has_citations:
        return
    (
        add_new_source_citation,
        add_existing_source_citation,
        add_existing_citation,
        add_zotero_citation,
        edit_citation,
        remove_citation,
    ) = callbacks
    menu = new_menu(
        "list-add",
        _("Add new citation for a new source"),
        add_new_source_citation,
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add new citation for an existing source"),
            add_existing_source_citation,
        )
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add an existing citation"),
            add_existing_citation,
        )
    )
    if zotero:
        menu.add(
            menu_item(
                "list-add",
                _("Add citation using Zotero"),
                add_zotero_citation,
            )
        )
    citation_list = grobject.obj.get_citation_list()
    if citation_list:
        removemenu = new_submenu(
            menu, "gramps-citation", _("Remove a citation")
        )
        add_double_separator(menu)
        work_list = []
        for handle in citation_list:
            citation = db.get_citation_from_handle(handle)
            text = citation_option_text(db, citation)
            work_list.append((text, citation))
        work_list.sort(key=lambda x: x[0])
        for text, citation in work_list:
            removemenu.add(
                menu_item("list-remove", text, remove_citation, citation)
            )
            menu.add(
                menu_item("gramps-citation", text, edit_citation, citation)
            )
    parent_menu.append(submenu_item("gramps-citation", _("Citations"), menu))


def add_notes_menu(
    parent_menu, db, grobject, callbacks, include_children=False
):
    """
    Build and add the notes submenu.
    """
    if not grobject.has_notes:
        return
    (
        add_new_note,
        add_existing_note,
        edit_note,
        remove_note,
    ) = callbacks
    menu = new_menu("list-add", _("Add a new note"), add_new_note)
    menu.add(
        menu_item("list-add", _("Add an existing note"), add_existing_note)
    )
    note_list = grobject.obj.get_note_list()
    if note_list:
        removemenu = new_submenu(menu, "gramps-notes", _("Remove a note"))
        add_double_separator(menu)
        note_list = get_sorted_notes(db, note_list)
        for text, note in note_list:
            removemenu.add(menu_item("list-remove", text, remove_note, note))
            menu.add(
                menu_item("gramps-notes", text, edit_note, note.get_handle())
            )
    if include_children:
        get_child_notes(menu, db, grobject, edit_note)
    parent_menu.append(submenu_item("gramps-notes", _("Notes"), menu))


def get_child_notes(menu, db, grobject, callback):
    """
    Find and add child notes to menu.
    """
    handle_list = []
    for child_obj in grobject.obj.get_note_child_list():
        for handle in child_obj.get_note_list():
            if handle not in handle_list:
                handle_list.append(handle)
    note_list = get_sorted_notes(db, handle_list)
    if note_list:
        add_double_separator(menu)
        for text, note in note_list:
            menu.add(
                menu_item("gramps-notes", text, callback, note.get_handle())
            )


def get_sorted_notes(db, handle_list):
    """
    Return a sorted note list.
    """
    note_list = []
    for handle in handle_list:
        note = db.get_note_from_handle(handle)
        notetype = str(note.get_type())
        text = note.get()[:40].replace("\n", " ")
        if len(text) > 39:
            text = "".join((text, "..."))
        text = ": ".join((notetype, text))
        note_list.append((text, note))
    note_list.sort(key=lambda x: x[0])
    return note_list


def add_privacy_menu_option(parent_menu, grobject, callback):
    """
    Build and add the privacy menu entry.
    """
    if grobject.obj.get_privacy():
        parent_menu.append(
            menu_item("gramps-unlock", _("Make public"), callback, False)
        )
    else:
        parent_menu.append(
            menu_item("gramps-lock", _("Make private"), callback, True)
        )


def add_clipboard_menu_option(parent_menu, callback):
    """
    Build and add the copy to clipboard menu entry.
    """
    parent_menu.append(
        menu_item("edit-copy", _("Copy to clipboard"), callback)
    )


def add_bookmark_menu_option(parent_menu, db, grobject, callback):
    """
    Build and add the bookmark menu entry.
    """
    found = False
    for bookmark in get_bookmarks(db, grobject.obj_type).get():
        if bookmark == grobject.obj.get_handle():
            found = True
            break
    if found:
        parent_menu.append(
            menu_item(
                "gramps-bookmark-delete", _("Unbookmark"), callback, False
            )
        )
    else:
        parent_menu.append(
            menu_item("gramps-bookmark", _("Bookmark"), callback, True)
        )


def add_tags_menu(parent_menu, db, grobject, callbacks, sort_by_name=False):
    """
    Build and add the tags submenu.
    """
    if not grobject.has_tags:
        return
    (
        new_tag,
        add_tag,
        organize_tags,
        remove_tag,
    ) = callbacks
    menu = Gtk.Menu()
    tag_add_list = []
    tag_remove_list = []
    for handle in db.get_tag_handles():
        tag = db.get_tag_from_handle(handle)
        if handle in grobject.obj.tag_list:
            tag_remove_list.append(tag)
        else:
            tag_add_list.append(tag)
    for tag_list in [tag_add_list, tag_remove_list]:
        if sort_by_name:
            tag_list.sort(key=lambda x: x.name)
        else:
            tag_list.sort(key=lambda x: x.priority)
    prepare_tag_menu_item(
        menu, tag_add_list, "list-add", _("Add a tag"), add_tag
    )
    prepare_tag_menu_item(
        menu, tag_remove_list, "list-remove", _("Remove a tag"), remove_tag
    )
    menu.add(menu_item("gramps-tag", _("Create new tag"), new_tag))
    menu.add(menu_item("gramps-tag", _("Organize tags"), organize_tags))
    parent_menu.append(submenu_item("gramps-tag", _("Tags"), menu))


def prepare_tag_menu_item(parent_menu, tag_list, icon_name, label, callback):
    """
    Prepare menu options for a tag action.
    """
    if tag_list:
        menu = Gtk.Menu()
        for tag in tag_list:
            menu.add(menu_item(icon_name, tag.name, callback, tag.handle))
        parent_menu.append(submenu_item("gramps-tag", label, menu))


def add_urls_menu(parent_menu, grobject, callbacks):
    """
    Build and add the urls submenu.
    """
    if not grobject.has_urls:
        return
    (
        add_url,
        edit_url,
        launch_url,
        remove_url,
    ) = callbacks
    menu = new_menu("list-add", _("Add a url"), add_url)
    if grobject.obj.get_url_list():
        editmenu = new_submenu(menu, "gramps-url", _("Edit a url"))
        removemenu = new_submenu(menu, "gramps-url", _("Remove a url"))
        add_double_separator(menu)
        url_list = []
        for url in grobject.obj.get_url_list():
            text = url.get_description()
            if not text:
                text = url.get_path()
            url_list.append((text, url))
        url_list.sort(key=lambda x: x[0])
        for text, url in url_list:
            editmenu.add(menu_item("gramps-url", text, edit_url, url))
            removemenu.add(menu_item("list-remove", text, remove_url, url))
            menu.add(menu_item("gramps-url", text, launch_url, url))
    parent_menu.append(submenu_item("gramps-url", _("Urls"), menu))


def add_media_menu(parent_menu, db, grobject, callbacks):
    """
    Build and add the media submenu.
    """
    if not grobject.has_media:
        return
    (
        add_new_media,
        add_existing_media,
        edit_media_ref,
        remove_media_ref,
    ) = callbacks
    menu = new_menu("list-add", _("Add a new media item"), add_new_media)
    menu.add(
        menu_item(
            "list-add",
            _("Add an existing media item"),
            add_existing_media,
        )
    )
    media_list = grobject.obj.get_media_list()
    if media_list:
        removemenu = new_submenu(
            menu, "gramps-media", _("Remove a media item")
        )
        add_double_separator(menu)
        for media_ref in media_list:
            media = db.get_media_from_handle(media_ref.ref)
            text = media.get_description()
            removemenu.add(
                menu_item("list-remove", text, remove_media_ref, media)
            )
            menu.add(menu_item("gramps-media", text, edit_media_ref, media))
    parent_menu.append(submenu_item("gramps-media", _("Media"), menu))


def add_names_menu(parent_menu, grobject, callbacks):
    """
    Build and add the names submenu.
    """
    (add_name, edit_name, remove_name) = callbacks
    menu = new_menu("list-add", _("Add a new name"), add_name)
    name_list = grobject.obj.get_alternate_names()
    if name_list:
        removemenu = new_submenu(menu, "gramps-person", _("Remove a name"))
        add_double_separator(menu)
        name = grobject.obj.get_primary_name()
        given_name = name.get_regular_name()
        menu.add(menu_item("gramps-person", given_name, edit_name, name))
        for name in name_list:
            given_name = name.get_regular_name()
            removemenu.add(
                menu_item("list-remove", given_name, remove_name, name)
            )
            menu.add(menu_item("gramps-person", given_name, edit_name, name))
    parent_menu.append(submenu_item("gramps-person", _("Names"), menu))


def add_associations_menu(parent_menu, db, grobject, callbacks):
    """
    Build and add the associations submenu.
    """
    (
        add_association_new_person,
        add_association_existing_person,
        edit_association,
        remove_association,
    ) = callbacks
    menu = new_menu(
        "list-add",
        _("Add an association for a new person"),
        add_association_new_person,
    )
    menu.add(
        menu_item(
            "list-add",
            _("Add an association for an existing person"),
            add_association_existing_person,
        )
    )
    person_ref_list = grobject.obj.get_person_ref_list()
    if person_ref_list:
        removemenu = new_submenu(
            menu, "gramps-person", _("Remove an association")
        )
        add_double_separator(menu)
        for person_ref in person_ref_list:
            person = db.get_person_from_handle(person_ref.ref)
            person_name = name_displayer.display(person)
            removemenu.add(
                menu_item(
                    "list-remove",
                    person_name,
                    remove_association,
                    person_ref,
                )
            )
            menu.add(
                menu_item(
                    "gramps-person",
                    person_name,
                    edit_association,
                    person_ref,
                )
            )
    parent_menu.append(submenu_item("gramps-person", _("Associations"), menu))


def add_parents_menu(parent_menu, db, grobject, callbacks):
    """
    Build and add the parents submenu.
    """
    (add_new_parents, add_existing_parents, edit_family) = callbacks
    menu = new_menu(
        "gramps-parents-add", _("Add a new set of parents"), add_new_parents
    )
    menu.add(
        menu_item(
            "gramps-parents-open",
            _("Add as child to an existing family"),
            add_existing_parents,
        )
    )
    parent_family_list = grobject.obj.get_parent_family_handle_list()
    if parent_family_list:
        menu.add(Gtk.SeparatorMenuItem())
        for handle in parent_family_list:
            family = db.get_family_from_handle(handle)
            family_text = family_name(family, db)
            menu.add(
                menu_item(
                    "gramps-parents",
                    family_text,
                    edit_family,
                    family,
                    "Family",
                )
            )
    parent_menu.append(submenu_item("gramps-parents", _("Parents"), menu))


def add_partners_menu(parent_menu, db, grobject, callbacks):
    """
    Build and add submenu the partners submenu.
    """
    (add_new_family, edit_family) = callbacks
    menu = new_menu(
        "gramps-spouse", _("Add as parent of new family"), add_new_family
    )
    family_list = grobject.obj.get_family_handle_list()
    if family_list:
        menu.add(Gtk.SeparatorMenuItem())
        for handle in family_list:
            family = db.get_family_from_handle(handle)
            family_text = family_name(family, db)
            menu.add(
                menu_item(
                    "gramps-spouse",
                    family_text,
                    edit_family,
                    family,
                    "Family",
                )
            )
    parent_menu.append(submenu_item("gramps-spouse", _("Spouses"), menu))


def add_participants_menu(parent_menu, callbacks, participants):
    """
    Build and add the participants submenu.
    """
    (
        add_new_participant,
        add_existing_participant,
        goto_person,
        edit_primary_object,
        edit_participant,
        remove_participant,
    ) = callbacks
    menu = new_menu(
        "gramps-person",
        _("Add a new person as a participant"),
        add_new_participant,
    )
    menu.add(
        menu_item(
            "gramps-person",
            _("Add an existing person as a participant"),
            add_existing_participant,
        )
    )
    if len(participants) > 1:
        gotomenu = new_submenu(menu, "gramps-person", _("Go to a participant"))
        editmenu = new_submenu(menu, "gramps-person", _("Edit a participant"))
        removemenu = new_submenu(
            menu, "gramps-person", _("Remove a participant")
        )
        add_double_separator(menu)
        participant_list = get_sorted_participants(participants)
        for (text, person, event_ref) in participant_list:
            handle = person.get_handle()
            gotomenu.add(menu_item("gramps-person", text, goto_person, handle))
            editmenu.add(
                menu_item(
                    "gramps-person",
                    text,
                    edit_primary_object,
                    person,
                    "Person",
                )
            )
            removemenu.add(
                menu_item(
                    "list-remove",
                    text,
                    remove_participant,
                    person,
                    event_ref,
                )
            )
            menu.add(
                menu_item(
                    "gramps-person",
                    text,
                    edit_participant,
                    person,
                    event_ref,
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


def add_repositories_menu(parent_menu, db, grobject, callbacks):
    """
    Build and add the repositories submenu.
    """
    (
        add_new_repository,
        add_existing_repository,
        edit_repo_ref,
        remove_repo_ref,
    ) = callbacks
    menu = new_menu("list-add", _("Add a new repository"), add_new_repository)
    menu.add(
        menu_item(
            "list-add",
            _("Add an existing repository"),
            add_existing_repository,
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
            removemenu.add(
                menu_item(
                    "list-remove",
                    repository_name,
                    remove_repo_ref,
                    repo_ref,
                )
            )
            menu.add(
                menu_item(
                    "gramps-repository",
                    repository_name,
                    edit_repo_ref,
                    repo_ref,
                )
            )
    parent_menu.append(
        submenu_item("gramps-repository", _("Repositories"), menu)
    )
