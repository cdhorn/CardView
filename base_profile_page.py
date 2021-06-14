# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2015-2016  Nick Hall
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
Combined View - Base page
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from html import escape
import pickle

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Gdk

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from gramps.gen.utils.callback import Callback
from gramps.gen.config import config
from gramps.gen.lib import (ChildRef, EventType, Family,
                            Name, Person, Surname)
from gramps.gen.db import DbTxn
from gramps.gui import widgets
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gui.editors import EditPerson, EditFamily, EditEvent, EditCitation
from gramps.gui.widgets.reorderfam import Reorder
from gramps.gui.selectors import SelectorFactory
from gramps.gen.errors import WindowActiveError
from gramps.gui.widgets import ShadeBox
from gramps.gui.ddtargets import DdTargets
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback,
                                 preset_name)
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gen.utils.file import media_path_full
from gramps.gui.utils import open_file_with_default_application
from gramps.gen.datehandler import displayer
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext


_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_SPACE = Gdk.keyval_from_name("space")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

def button_activated(event, mouse_button):
    if (event.type == Gdk.EventType.BUTTON_PRESS and
        event.button == mouse_button) or \
       (event.type == Gdk.EventType.KEY_PRESS and
        event.keyval in (_RETURN, _KP_ENTER, _SPACE)):
        return True
    else:
        return False


class BaseProfilePage(Callback):

    __signals__ = {
        'object-changed' : (str, str),
        }

    def __init__(self, dbstate, uistate, addon_config):
        Callback.__init__(self)

        self.dbstate = dbstate
        self.uistate = uistate
        self._config = addon_config
        self.handle = None

        self.config_update()

    def config_update(self):
        pass

    def get_handle(self):
        return self.handle

    def make_dragbox(self, box, dragtype, handle):
        eventbox = ShadeBox(self.use_shade)
        eventbox.add(box)

        if handle is not None:
            if dragtype == 'Person':
                self._set_draggable(eventbox, handle, DdTargets.PERSON_LINK, 'gramps-person')
            elif dragtype == 'Family':
                self._set_draggable(eventbox, handle, DdTargets.FAMILY_LINK, 'gramps-family')
            elif dragtype == 'Event':
                self._set_draggable(eventbox, handle, DdTargets.EVENT, 'gramps-event')
            elif dragtype == 'Citation':
                self._set_draggable(eventbox, handle, DdTargets.CITATION_LINK, 'gramps-citation')

        return eventbox

    def _set_draggable(self, eventbox, object_h, dnd_type, stock_icon):
        """
        Register the given eventbox as a drag_source with given object_h
        """
        eventbox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                 [], Gdk.DragAction.COPY)
        tglist = Gtk.TargetList.new([])
        tglist.add(dnd_type.atom_drag_type,
                   dnd_type.target_flags,
                   dnd_type.app_id)
        eventbox.drag_source_set_target_list(tglist)
        eventbox.drag_source_set_icon_name(stock_icon)
        eventbox.connect('drag_data_get',
                         self._make_drag_data_get_func(object_h, dnd_type))

    def _make_drag_data_get_func(self, object_h, dnd_type):
        """
        Generate at runtime a drag_data_get function returning the given dnd_type and object_h
        """
        def drag_data_get(widget, context, sel_data, info, time):
            if info == dnd_type.app_id:
                data = (dnd_type.drag_type, id(self), object_h, 0)
                sel_data.set(dnd_type.atom_drag_type, 8, pickle.dumps(data))
        return drag_data_get


    def reorder_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *obj):
        if self.handle:
            try:
                Reorder(self.dbstate, self.uistate, [], self.handle)
            except WindowActiveError:
                pass

    def _person_link(self, obj, event, handle):
        self._link(event, 'Person', handle)

    def _event_link(self, obj, event, handle):
        self._link(event, 'Event', handle)

    def _link(self, event, obj_type, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.emit('object-changed', (obj_type, handle))

