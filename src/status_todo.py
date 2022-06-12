#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022   Christopher Horn
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
To do note status indicator plugin.
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
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Family, NoteType, Person
from gramps.gui.editors import EditNote

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from view.common.common_classes import GrampsBaseIcon
from view.common.common_utils import describe_object
from view.config.config_utils import create_grid
from view.menus.menu_utils import menu_item, show_menu

_ = glocale.translation.sgettext

OPTION_TODO = "status.todo"
OPTION_TODO_EDIT = "status.todo-edit"
OPTION_TODO_PERSON = "status.todo-person"
OPTION_TODO_FAMILY = "status.todo-family"


# ------------------------------------------------------------------------
#
# Status plugin API consists of a dictionary with the supported types,
# default options, callable to build configuration grids for the options,
# and callable to check status and return any icons as needed.
#
# ------------------------------------------------------------------------
def load_on_reg(_dummy_dbstate, _dummy_uistate, _dummy_plugin):
    """
    Return status plugin attributes.
    """
    return [
        {
            "supported_types": supported_types,
            "default_options": default_options,
            "get_config_grids": build_todo_grid,
            "get_status": get_todo_status,
        }
    ]


# ------------------------------------------------------------------------
#
# Object types supported by this status plugin
#
# ------------------------------------------------------------------------
supported_types = [
    "Address",
    "Attribute",
    "Citation",
    "ChildRef",
    "Event",
    "EventRef",
    "Family",
    "LdsOrd",
    "Media",
    "MediaRef",
    "Name",
    "Person",
    "PersonRef",
    "Place",
    "Repository",
    "RepoRef",
    "Source",
]


# ------------------------------------------------------------------------
#
# Default options for this status plugin
#
# ------------------------------------------------------------------------
default_options = [
    (OPTION_TODO, True),
    (OPTION_TODO_EDIT, False),
    (OPTION_TODO_PERSON, False),
    (OPTION_TODO_FAMILY, False),
]


# ------------------------------------------------------------------------
#
# Function to build and return configuration grid for the options.
#
# ------------------------------------------------------------------------
def build_todo_grid(configdialog, _dummy_grstate):
    """
    Build status indicator configuration section.
    """
    grid = create_grid()
    configdialog.add_text(grid, _("To Do Indicator"), 0, bold=True)
    configdialog.add_checkbox(
        grid,
        _("Enable to do indicator icon"),
        1,
        OPTION_TODO,
    )
    configdialog.add_checkbox(
        grid,
        _("Open note in editor instead of navigating to note page"),
        2,
        OPTION_TODO_EDIT,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable full person to do evaluation"),
        3,
        OPTION_TODO_PERSON,
    )
    configdialog.add_checkbox(
        grid,
        _("Enable full family to do evaluation"),
        4,
        OPTION_TODO_FAMILY,
    )
    return grid


# ------------------------------------------------------------------------
#
# Function to check status and return icons as needed.
#
# ------------------------------------------------------------------------
def get_todo_status(grstate, obj, size):
    """
    Load todo status indicator if needed.
    """
    if not grstate.config.get(OPTION_TODO):
        return []

    todo_list = []
    db = grstate.dbstate.db
    obj_path = [describe_object(db, obj)]

    done = False
    if isinstance(obj, Person) and grstate.config.get(OPTION_TODO_PERSON):
        evaluate_person(db, obj, obj_path, todo_list)
        done = True
    elif isinstance(obj, Family) and grstate.config.get(OPTION_TODO_FAMILY):
        evaluate_family(db, obj, obj_path, todo_list)
        done = True
    if not done:
        evaluate_object(db, obj, obj_path, todo_list)

    if todo_list:
        todo_icon = GrampsToDoIcon(grstate, todo_list, size)
        return [todo_icon]
    return []


# ------------------------------------------------------------------------
#
# Some helper functions.
#
# ------------------------------------------------------------------------
def evaluate_family(db, obj, obj_path, todo_list):
    """
    Evaluate all members of a family in case any have open todo items.
    """
    get_event_from_handle = db.get_event_from_handle
    get_person_from_handle = db.get_person_from_handle
    new_obj_path = evaluate_obj_path(db, obj, obj_path)
    evaluate_object(db, obj, new_obj_path, todo_list)
    for event_ref in obj.event_ref_list:
        event = get_event_from_handle(event_ref.ref)
        evaluate_object(db, event, obj_path, todo_list)
    if obj.father_handle:
        father = get_person_from_handle(obj.father_handle)
        evaluate_person(
            db,
            father,
            new_obj_path,
            todo_list,
            include_parents=False,
            include_family=False,
        )
    if obj.mother_handle:
        mother = get_person_from_handle(obj.mother_handle)
        evaluate_person(
            db,
            mother,
            new_obj_path,
            todo_list,
            include_parents=False,
            include_family=False,
        )
    for child_ref in obj.child_ref_list:
        person = get_person_from_handle(child_ref.ref)
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
    get_event_from_handle = db.get_event_from_handle
    for event_ref in obj.event_ref_list:
        event = get_event_from_handle(event_ref.ref)
        evaluate_object(db, event, obj_path, todo_list)
    get_media_from_handle = db.get_media_from_handle
    for media_ref in obj.media_list:
        media = get_media_from_handle(media_ref.ref)
        evaluate_object(db, media, obj_path, todo_list)
    get_family_from_handle = db.get_family_from_handle
    if include_family:
        get_family_from_handle = db.get_family_from_handle
        for handle in obj.family_list:
            family = get_family_from_handle(handle)
            evaluate_object(db, family, obj_path, todo_list)
            for event_ref in family.event_ref_list:
                evaluate_event(db, event_ref.ref, obj_path, todo_list)
    if include_parents:
        person_handle = obj.handle
        for handle in obj.parent_family_list:
            family = get_family_from_handle(handle)
            for child_ref in family.child_ref_list:
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
    for handle in obj.note_list:
        evaluate_note(db, handle, new_obj_path, todo_list)
    for child_obj in obj.get_note_child_list():
        new_obj_path = obj_path + [describe_object(db, child_obj)]
        for handle in child_obj.note_list:
            evaluate_note(db, handle, new_obj_path, todo_list)


def evaluate_note(db, handle, obj_path, todo_list):
    """
    Evaluate whether it is a to do note.
    """
    note = db.get_note_from_handle(handle)
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


# ------------------------------------------------------------------------
#
# ToDoIcon class
#
# ------------------------------------------------------------------------
class GrampsToDoIcon(GrampsBaseIcon):
    """
    A class to manage the icon and enable access to the to do items.
    """

    def __init__(self, grstate, todo_list, size):
        if len(todo_list) > 1:
            tooltip = "%s %s" % (str(len(todo_list)), _("To Do Tasks"))
        else:
            tooltip = "1 %s" % _("To Do Task")
        GrampsBaseIcon.__init__(
            self, grstate, "task-due", size=size, tooltip=tooltip
        )
        self.todo_list = todo_list

    def icon_clicked(self, event):
        """
        Build to do context menu.
        """
        menu = Gtk.Menu()
        if self.grstate.config.get(OPTION_TODO_EDIT):
            callback = self.edit_note
        else:
            callback = self.goto_note
        for (obj_path, note) in self.todo_list:
            text = "->".join(tuple(obj_path))
            text = "->".join((text, _("Note")))
            text = "%s %s" % (text, note.gramps_id)
            menu.append(menu_item("task-due", text, callback, note))
        return show_menu(menu, self, event)

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
