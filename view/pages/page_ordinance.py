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
LDSOrdinance Profile Page
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
from ..common.common_classes import GrampsOptions
from ..common.common_const import _LEFT_BUTTON
from ..common.common_utils import button_activated, get_gramps_object_type
from ..frames.frame_couple import CoupleGrampsFrame
from ..frames.frame_ordinance import LDSOrdinanceGrampsFrame
from ..frames.frame_person import PersonGrampsFrame
from .page_base import BaseProfilePage
from .page_const import FRAME_MAP

_ = glocale.translation.sgettext


class LDSOrdinanceProfilePage(BaseProfilePage):
    """
    Provides the LDS ordinance profile page view with information about
    the ordinance of a person or spouse.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
        self.order_action = None
        self.family_action = None
        self.reorder_sensitive = None
        self.child = None
        self.colors = None
        self.active_profile = None
        self.focus_type = "Person"

    @property
    def obj_type(self):
        return self.focus_type

    @property
    def page_type(self):
        return "LdsOrd"

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, context):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not context:
            return

        primary = context.primary_obj.obj
        ldsord = context.secondary_obj.obj
        
        self.focus_type = get_gramps_object_type(primary)

        (option, frame) = FRAME_MAP[self.focus_type]
        groptions = GrampsOptions(option)
        self.active_profile = frame(self.grstate, groptions, primary)

        groptions = GrampsOptions("options.active.ldsord")
        frame = LDSOrdinanceGrampsFrame(
            self.grstate, groptions, primary, ldsord
        )

        groups = self.config.get("options.page.ldsord.layout.groups").split(
            ","
        )
        obj_groups = self.get_object_groups(groups, ldsord)
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
        return
