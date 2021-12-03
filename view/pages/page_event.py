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
Event Profile Page
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.uimanager import ActionGroup

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..frames.frame_event import EventGrampsFrame
from ..groups.group_utils import get_references_group
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class EventProfilePage(BaseProfilePage):
    """
    Provides the event profile page view with information about the event.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
        self.active_profile = None

    @property
    def obj_type(self):
        """
        Primary object type underpinning page.
        """
        return "Event"

    @property
    def page_type(self):
        """
        Page type.
        """
        return "Event"

    def define_actions(self, view):
        """
        Define page specific actions.
        """
        self.action_group = ActionGroup(name="Event")
        self.action_group.add_actions(
            [
                ("AddNewPart", self._add_new_participant),
                ("AddExistingPart", self._add_existing_participant),
            ]
        )
        view.add_action_group(self.action_group)

    def render_page(self, header, vbox, context):
        """
        Render the page contents.
        """
        if not context:
            return

        event = context.primary_obj.obj

        groptions = GrampsOptions("options.active.event")
        self.active_profile = EventGrampsFrame(
            self.grstate,
            groptions,
            event,
        )

        groups = self.config.get("options.page.event.layout.groups").split(",")
        obj_groups = self.get_object_groups(
            groups, event, age_base=event.get_date_object()
        )

        people_list = []
        family_list = []
        if "people" in groups or "family" in groups:
            for (
                obj_type,
                obj_handle,
            ) in self.grstate.dbstate.db.find_backlink_handles(
                event.get_handle()
            ):
                if obj_type == "Person" and obj_handle not in people_list:
                    people_list.append(("Person", obj_handle))
                elif obj_type == "Family" and obj_handle not in family_list:
                    family_list.append(("Family", obj_handle))

        if people_list:
            groptions = GrampsOptions("options.group.people")
            args = {
                "title": (
                    _("Individual Participants"),
                    _("Individual Participants"),
                )
            }
            obj_groups.update(
                {
                    "people": get_references_group(
                        self.grstate,
                        None,
                        args,
                        groptions=groptions,
                        obj_list=people_list,
                        age_base=event.get_date_object(),
                    )
                }
            )
        if family_list:
            groptions = GrampsOptions("options.group.family")
            args = {
                "title": (_("Family Participants"), _("Family Participants"))
            }
            obj_groups.update(
                {
                    "family": get_references_group(
                        self.grstate,
                        None,
                        args,
                        groptions=groptions,
                        obj_list=family_list,
                        age_base=event.get_date_object(),
                    )
                }
            )

        body = self.render_group_view(obj_groups)
        if self.config.get("options.global.pin-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        self.add_media_bar(vbox, event)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
