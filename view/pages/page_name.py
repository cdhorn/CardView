# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
Name Profile Page
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import hashlib

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.errors import WindowActiveError
from gramps.gui.uimanager import ActionGroup
from gramps.gui.widgets.reorderfam import Reorder

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..frames.frame_classes import GrampsOptions
from ..frames.frame_const import _LEFT_BUTTON
from ..frames.frame_name import NameGrampsFrame
from ..frames.frame_person import PersonGrampsFrame
from ..frames.frame_utils import button_activated
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class NameProfilePage(BaseProfilePage):
    """
    Provides the name profile page view with information about the
    name of a person.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
        self.order_action = None
        self.family_action = None
        self.reorder_sensitive = None
        self.child = None
        self.colors = None
        self.active_profile = None

    @property
    def obj_type(self):
        return "Person"

    @property
    def page_type(self):
        return "Name"

    def define_actions(self, view):
        self.order_action = ActionGroup(name="ChangeOrder")
        self.order_action.add_actions([("ChangeOrder", self.reorder)])

        self.family_action = ActionGroup(name="Family")
        self.family_action.add_actions(
            [
                ("AddSpouse", self.add_spouse),
                ("AddParents", self.add_parents),
                ("ShareFamily", self.select_parents),
            ]
        )

        view._add_action_group(self.order_action)
        view._add_action_group(self.family_action)

    def enable_actions(self, uimanager, person):
        uimanager.set_actions_visible(self.family_action, True)
        uimanager.set_actions_visible(self.order_action, True)

    def disable_actions(self, uimanager):
        uimanager.set_actions_visible(self.family_action, False)
        uimanager.set_actions_visible(self.order_action, False)

    def render_page(self, header, vbox, person, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not person or not secondary:
            return

        name = person.get_primary_name()
        sha256_hash = hashlib.sha256()
        sha256_hash.update(str(name.serialize()).encode("utf-8"))
        if sha256_hash.hexdigest() != secondary:
            for name in person.get_alternate_names():
                sha256_hash = hashlib.sha256()
                sha256_hash.update(str(name.serialize()).encode("utf-8"))
                if sha256_hash.hexdigest() == secondary:
                    break

        groptions = GrampsOptions("options.active.person")
        self.active_profile = PersonGrampsFrame(
            self.grstate, groptions, person
        )

        groptions = GrampsOptions("options.active.name")
        frame = NameGrampsFrame(self.grstate, groptions, person, name)

        groups = self.config.get("options.page.name.layout.groups").split(",")
        obj_groups = self.get_object_groups(groups, name)
        body = self.render_group_view(obj_groups)

        if self.config.get("options.global.pin-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.pack_start(frame, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
            vbox.pack_start(frame, False, False, 0)
        self.child = body
        vbox.pack_start(self.child, True, True, 0)
        vbox.show_all()

        family_handle_list = person.get_parent_family_handle_list()
        self.reorder_sensitive = len(family_handle_list) > 1
        family_handle_list = person.get_family_handle_list()
        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list) > 1
        return

    def reorder_button_press(self, obj, event, _dummy_handle):
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *_dummy_obj):
        if self.active_profile:
            try:
                Reorder(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.active_profile.obj.get_handle(),
                )
            except WindowActiveError:
                pass

    def add_spouse(self, *_dummy_obj):
        if self.active_profile:
            self.active_profile.add_new_spouse()

    def select_parents(self, *_dummy_obj):
        if self.active_profile:
            self.active_profile.add_existing_parents()

    def add_parents(self, *_dummy_obj):
        if self.active_profile:
            self.active_profile.add_new_parents()
