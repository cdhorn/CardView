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
Person Profile Page
"""

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
from ..common.common_classes import GrampsOptions
from ..common.common_const import _LEFT_BUTTON
from ..common.common_utils import button_activated
from ..frames.frame_person import PersonGrampsFrame
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class PersonProfilePage(BaseProfilePage):
    """
    Provides the person profile page view with information about the person.
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
        """
        Primary object type underpinning the page.
        """
        return "Person"

    @property
    def page_type(self):
        """
        Page type.
        """
        return "Person"

    def define_actions(self, view):
        """
        Define page specific actions.
        """
        self.order_action = ActionGroup(name="ChangeOrder")
        self.order_action.add_actions([("ChangeOrder", self.reorder)])

        self.family_action = ActionGroup(name="Family")
        self.family_action.add_actions(
            [
                ("AddSpouse", self.add_new_family),
                ("AddParents", self.add_new_parents),
                ("ShareFamily", self.add_existing_parents),
            ]
        )
        self.person_action = ActionGroup(name="Person")
        self.person_action.add_actions(
            [("SetActive", self.set_default_person)]
        )
        view.add_action_group(self.order_action)
        view.add_action_group(self.family_action)
        view.add_action_group(self.person_action)

    def enable_actions(self, uimanager, _dummy_obj):
        """
        Enable page specific actions.
        """
        uimanager.set_actions_visible(self.person_action, True)
        uimanager.set_actions_visible(self.family_action, True)
        uimanager.set_actions_visible(self.order_action, True)

    def disable_actions(self, uimanager):
        """
        Disable page specific actions.
        """
        uimanager.set_actions_visible(self.person_action, False)
        uimanager.set_actions_visible(self.family_action, False)
        uimanager.set_actions_visible(self.order_action, False)

    def render_page(self, header, vbox, context):
        """
        Render the page contents.
        """
        if not context:
            return

        person = context.primary_obj.obj

        groptions = GrampsOptions("options.active.person")
        self.active_profile = PersonGrampsFrame(
            self.grstate, groptions, person
        )

        groups = self.config.get("options.page.person.layout.groups").split(
            ","
        )
        obj_groups = self.get_object_groups(groups, person)
        body = self.render_group_view(obj_groups)

        if self.config.get("options.global.pin-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        self.add_media_bar(vbox, person)
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
        """
        Trigger reorder families.
        """
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *_dummy_obj):
        """
        Reorder families.
        """
        if self.active_profile:
            try:
                Reorder(
                    self.grstate.dbstate,
                    self.grstate.uistate,
                    [],
                    self.active_profile.primary.obj.get_handle(),
                )
            except WindowActiveError:
                pass

    def add_new_family(self, *_dummy_obj):
        """
        Add new family with or without spouse.
        """
        if self.active_profile:
            self.active_profile.add_new_family()

    def add_existing_parents(self, *_dummy_obj):
        """
        Add an existing set of parents.
        """
        if self.active_profile:
            self.active_profile.add_existing_parents()

    def add_new_parents(self, *_dummy_obj):
        """
        Add a new set of parents.
        """
        if self.active_profile:
            self.active_profile.add_new_parents()

    def set_default_person(self, *_dummy_obj):
        """
        Set new default person.
        """
        if self.active_profile:
            self.active_profile.set_default_person()
