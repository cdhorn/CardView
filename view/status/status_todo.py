#
# Gramps - a GTK+/GNOME based genealogy program
#
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
To do status indicator.
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
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Family, NoteType, Person
from gramps.gui.editors import EditNote

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsBaseIcon
from ..common.common_utils import describe_object, menu_item

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# GrampsToDoIcon class
#
# ------------------------------------------------------------------------
class GrampsToDoIcon(GrampsBaseIcon):
    """
    A class to manage the icon and access to the to do items.
    """

    def __init__(self, grstate, todo_list):
        if len(todo_list) > 1:
            tooltip = " ".join((str(len(todo_list)), _("To Do Tasks")))
        else:
            tooltip = " ".join(("1", _("To Do Task")))
        GrampsBaseIcon.__init__(self, grstate, "task-due", tooltip=tooltip)
        self.todo_list = todo_list

    def icon_clicked(self, event):
        """
        Build to do context menu.
        """
        menu = Gtk.Menu()
        if self.grstate.config.get("options.global.status.todo-edit"):
            callback = self.edit_note
        else:
            callback = self.goto_note
        for (obj_path, note) in self.todo_list:
            text = "->".join(tuple(obj_path))
            text = "->".join((text, _("Note")))
            text = " ".join((text, note.get_gramps_id()))
            menu.append(menu_item("task-due", text, callback, note))
        menu.attach_to_widget(self, None)
        menu.show_all()
        if Gtk.get_minor_version() >= 22:
            menu.popup_at_pointer(event)
        else:
            menu.popup(None, None, None, None, event.button, event.time)
        return True

    def goto_note(self, _dummy_event, note):
        """
        Go to the note page.
        """
        self.grstate.load_primary_page("Note", note)

    def edit_note(self, _dummy_event, note):
        """
        Open note in editor.
        """
        try:
            EditNote(
                self.grstate.dbstate,
                self.grstate.uistate,
                [],
                note,
            )
        except WindowActiveError:
            pass


def get_todo_status(grstate, obj):
    """
    Load todo status indicator if needed.
    """
    if not grstate.config.get("options.global.status.todo"):
        return []

    todo_list = []
    db = grstate.dbstate.db
    obj_path = [describe_object(db, obj)]

    done = False
    if isinstance(obj, Person):
        if grstate.config.get("options.global.status.todo-person"):
            evaluate_person(db, obj, obj_path, todo_list)
            done = True
    elif isinstance(obj, Family):
        if grstate.config.get("options.global.status.todo-family"):
            evaluate_family(db, obj, obj_path, todo_list)
            done = True
    if not done:
        evaluate_object(db, obj, obj_path, todo_list)

    if todo_list:
        todo_icon = GrampsToDoIcon(grstate, todo_list)
        return [todo_icon]
    return []


def evaluate_family(db, obj, obj_path, todo_list):
    """
    Evaluate all members of a family in case any have open todo items.
    """
    new_obj_path = evaluate_obj_path(db, obj, obj_path)
    evaluate_object(db, obj, new_obj_path, todo_list)
    for event_ref in obj.get_event_ref_list():
        event = db.get_event_from_handle(event_ref.ref)
        evaluate_object(db, event, obj_path, todo_list)
    father_handle = obj.get_father_handle()
    if father_handle:
        father = db.get_person_from_handle(father_handle)
        evaluate_person(
            db,
            father,
            new_obj_path,
            todo_list,
            include_parents=False,
            include_family=False,
        )
    mother_handle = obj.get_mother_handle()
    if mother_handle:
        mother = db.get_person_from_handle(mother_handle)
        evaluate_person(
            db,
            mother,
            new_obj_path,
            todo_list,
            include_parents=False,
            include_family=False,
        )
    for child_ref in obj.get_child_ref_list():
        person = db.get_person_from_handle(child_ref.ref)
        evaluate_person(
            db, person, new_obj_path, todo_list, include_parents=False
        )


def evaluate_person(
    db, obj, obj_path, todo_list, include_parents=True, include_family=True
):
    """
    Evaluate base person and then all their details for open todo items.
    """
    new_obj_path = evaluate_obj_path(db, obj, obj_path)
    evaluate_object(db, obj, new_obj_path, todo_list)
    evaluate_person_details(
        db,
        obj,
        new_obj_path,
        todo_list,
        include_parents=include_parents,
        include_family=include_family,
    )


def evaluate_person_details(
    db, obj, obj_path, todo_list, include_parents=True, include_family=True
):
    """
    Evaluate all events and families a person may head as well as their
    child references from parent families to determine if any to do items
    exist for any aspect of that person.
    """
    for event_ref in obj.get_event_ref_list():
        event = db.get_event_from_handle(event_ref.ref)
        evaluate_object(db, event, obj_path, todo_list)
    #        evaluate_event(db, event_ref.ref, obj_path, todo_list)
    for media_ref in obj.get_media_list():
        media = db.get_media_from_handle(media_ref.ref)
        evaluate_object(db, media, obj_path, todo_list)
    if include_family:
        for handle in obj.get_family_handle_list():
            family = db.get_family_from_handle(handle)
            evaluate_object(db, family, obj_path, todo_list)
            for event_ref in family.get_event_ref_list():
                evaluate_event(db, event_ref.ref, obj_path, todo_list)
    if include_parents:
        person_handle = obj.get_handle()
        for handle in obj.get_parent_family_handle_list():
            family = db.get_family_from_handle(handle)
            for child_ref in family.get_child_ref_list():
                if child_ref.ref == person_handle:
                    evaluate_object(db, child_ref, obj_path, todo_list)


def evaluate_event(db, handle, obj_path, todo_list):
    """
    Evaluate whether event has any todo notes.
    """
    event = db.get_event_from_handle(handle)
    new_obj_path = evaluate_obj_path(db, event, obj_path)
    evaluate_object(db, event, new_obj_path, todo_list)


def evaluate_object(db, obj, obj_path, todo_list):
    """
    Evaluate whether object has any todo notes.
    """
    new_obj_path = evaluate_obj_path(db, obj, obj_path)
    for handle in obj.get_note_list():
        note = db.get_note_from_handle(handle)
        evaluate_note(db, note, new_obj_path, todo_list)
    for child_obj in obj.get_note_child_list():
        new_obj_path = obj_path + [describe_object(db, child_obj)]
        for handle in child_obj.get_note_list():
            note = db.get_note_from_handle(handle)
            evaluate_note(db, note, new_obj_path, todo_list)


def evaluate_note(db, note, obj_path, todo_list):
    """
    Evaluate whether it is a to do note.
    """
    if note.get_type() == NoteType.TODO:
        todo_list.append((obj_path, note))


def evaluate_obj_path(db, obj, obj_path):
    """
    Evaluate and return updated path if needed.
    """
    new_obj = describe_object(db, obj)
    if obj_path[-1] != new_obj:
        return obj_path + [new_obj]
    return obj_path
