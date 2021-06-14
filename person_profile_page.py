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
Person Profile Page
"""

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from html import escape
from operator import itemgetter
import re

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
from gi.repository import Gtk
from gi.repository import Pango

#-------------------------------------------------------------------------
#
# Gramps Modules
#
#-------------------------------------------------------------------------
from taglist import TagList
from combined_timeline import Timeline
from base_profile_page import BaseProfilePage

from gramps.gen.lib.date import Today
from gramps.gui.display import display_url
from gramps.gui.uimanager import ActionGroup

from gramps.gen.config import config
from gramps.gen.lib import (EventRoleType, EventType, FamilyRelType, Person, Family, ChildRef, Span)
from gramps.gui.editors import EditFamily
from gramps.gen.errors import WindowActiveError
from gramps.gui.selectors import SelectorFactory
from gramps.gui import widgets
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback)
from gramps.gen.utils.db import get_participant_from_event
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.thumbnails import (SIZE_NORMAL, SIZE_LARGE)
from gramps.gui.widgets.styledtexteditor import StyledTextEditor
from gramps.gen.datehandler import displayer
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext

from gramps.gen.relationship import get_relationship_calculator

from frame_image import ImageFrame
from frame_person import PersonProfileFrame
from frame_css import add_style_double_frame, add_style_single_frame

from frame_groups import get_parent_profiles, get_spouse_profiles, get_citation_profiles, get_timeline_profiles


URL_MATCH = re.compile(r'https?://[^\s]+')

class PersonProfilePage(BaseProfilePage):

    def __init__(self, dbstate, uistate, config):
        BaseProfilePage.__init__(self, dbstate, uistate, config)
        self.reorder_sensitive = True

    def obj_type(self):
        return 'Person'

    def config_update(self):
        pass
    
    def define_actions(self, view):
        self.order_action = ActionGroup(name='ChangeOrder')
        self.order_action.add_actions([
            ('ChangeOrder', self.reorder)])

        self.family_action = ActionGroup(name='Family')
        self.family_action.add_actions([
            ('AddSpouse', self.add_spouse),
            ('AddParents', self.add_parents),
            ('ShareFamily', self.select_parents)])

        view._add_action_group(self.order_action)
        view._add_action_group(self.family_action)

    def enable_actions(self, uimanager, person):
        uimanager.set_actions_visible(self.family_action, True)
        uimanager.set_actions_visible(self.order_action, True)

    def disable_actions(self, uimanager):
        uimanager.set_actions_visible(self.family_action, False)
        uimanager.set_actions_visible(self.order_action, False)

    def display_profile(self, person):

        self.handle = person.handle
        
        panel = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        vbox = Gtk.VBox(spacing=3)
        panel.add_with_viewport(vbox)

        hbox = Gtk.HBox()
        home = self.dbstate.db.get_default_person()
        self.active_profile = PersonProfileFrame(self.dbstate, self.uistate, person, "active", "preferences.profile.person", self._config, self.link_router, relation=home)
        if self._config.get("preferences.profile.person.active.show-image"):
            image = ImageFrame(self.dbstate.db, self.uistate, person, size=bool(self._config.get("preferences.profile.person.active.show-image-large")))
            if self._config.get("preferences.profile.person.active.show-image-first"): 
                hbox.pack_start(image, expand=False, fill=True, padding=0)
                add_style_double_frame(image, self.active_profile)
        hbox.pack_start(self.active_profile, expand=True, fill=True, padding=0)
        if self._config.get("preferences.profile.person.active.show-image"):
            if not self._config.get("preferences.profile.person.active.show-image-first"):            
                hbox.pack_end(image, expand=False, fill=True, padding=0)
                add_style_double_frame(self.active_profile, image)
        else:
            add_style_single_frame(self.active_profile)
        vbox.pack_start(hbox, expand=True, fill=True, padding=0)
        
        hbox = Gtk.HBox(expand=True, spacing=3)
        vbox.pack_start(hbox, expand=True, fill=True, padding=0)

        parents_box = Gtk.VBox(spacing=3)
        parents = get_parent_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
        if parents is not None:
            parents_box.pack_start(parents, expand=False, fill=False, padding=0)

        spouses_box = Gtk.VBox(spacing=3)
        spouses = get_spouse_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
        if spouses is not None:
            spouses_box.pack_start(spouses, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.show-timeline"):            
            timeline_box = Gtk.VBox(spacing=3)
            timeline = get_timeline_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
            if timeline is not None:
                timeline_box.pack_start(timeline, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.show-citations"):
            citations_box = Gtk.VBox(spacing=3)
            citations = get_citation_profiles(self.dbstate, self.uistate, person, router=self.link_router, config=self._config)
            if citations is not None:
                citations_box.pack_start(citations, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.families-stacked"):
            families_box = Gtk.VBox(spacing=3)
            families_box.pack_start(parents_box, expand=False, fill=False, padding=0)
            families_box.pack_start(spouses_box, expand=False, fill=False, padding=0)
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                hbox.pack_start(families_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-timeline"):
                hbox.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-citations"):
                hbox.pack_start(citations_box, expand=True, fill=True, padding=0)
            if not self._config.get("preferences.profile.person.layout.spouses-left"):
                hbox.pack_start(families_box, expand=True, fill=True, padding=0)
        else:
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                hbox.pack_start(spouses_box, expand=True, fill=True, padding=0)
            else:
                hbox.pack_start(parents_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-timeline"):
                hbox.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-citations"):
                hbox.pack_start(citations_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                hbox.pack_start(parents_box, expand=True, fill=True, padding=0)
            else:
                hbox.pack_start(spouses_box, expand=True, fill=True, padding=0)

        mbox = Gtk.Box()
        mbox.add(panel)
        mbox.show_all()
        return mbox

    def link_router(self, obj, event, handle, action):
        if action == "link-person":
            self._link(event, "Person", handle)
        elif action == "edit-person":
            self.edit_person(handle)
        elif action == "edit-family":
            self.edit_family(handle)
        elif action == "edit-event":
            self.edit_event(handle)
        elif action == "edit-citation":
            self.edit_citation(handle)


    def get_url(self, citation):
        for handle in citation.get_note_list():
            note = self.dbstate.db.get_note_from_handle(handle)
            text = note.get()
            url_match = re.compile(r'https?://[^\s]+')
            result = URL_MATCH.search(text)
            if result:
                url = result.group(0)
                link_func = lambda x,y,z: display_url(url)
                name = (url, None)
                link_label = widgets.LinkLabel(name, link_func, None, False,
                                       theme=self.theme)
                link_label.set_tooltip_text(_('Click to visit this link'))
                return link_label
        return None


##############################################################################
#
# Toolbar actions
#
##############################################################################

    def edit_active(self, *obj):
        self.edit_person(self.handle)

    def add_spouse(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_spouse()
            
    def select_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_existing_parents()
            
    def add_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_parents()
            
    def add_tag(self, trans, object_handle, tag_handle):
        """
        Add the given tag to the active object.
        """
        person = self.dbstate.db.get_person_from_handle(object_handle)
        person.add_tag(tag_handle)
        self.dbstate.db.commit_person(person, trans)

