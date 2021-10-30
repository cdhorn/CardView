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
Tag Profile Page
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..common.common_classes import GrampsOptions
from ..frames.frame_tag import TagGrampsFrame
from ..groups.group_utils import get_references_group
from .page_base import BaseProfilePage
from .page_const import LABELS

_ = glocale.translation.sgettext


class TagProfilePage(BaseProfilePage):
    """
    Provides the tag profile page view with information about the tagged
    objects.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)

    @property
    def obj_type(self):
        return "Person"

    @property
    def page_type(self):
        return "Tag"

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, obj, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not secondary:
            return
        tag = self.grstate.dbstate.db.get_tag_from_handle(secondary)

        groptions = GrampsOptions("options.active.tag")
        self.active_profile = TagGrampsFrame(self.grstate, groptions, tag)

        groups = self.config.get("options.page.tag.layout.groups").split(",")
        obj_groups = {}

        object_list = {}
        for (
            obj_type,
            obj_handle,
        ) in self.grstate.dbstate.db.find_backlink_handles(tag.get_handle()):
            if obj_type not in object_list:
                object_list.update({obj_type: []})
            object_list[obj_type].append((obj_type, obj_handle))

        if object_list:
            for key in object_list:
                groptions = GrampsOptions(
                    "options.group.{}".format(key.lower())
                )
                obj_groups.update(
                    {
                        key.lower(): get_references_group(
                            self.grstate,
                            None,
                            groptions=groptions,
                            title_plural=LABELS[key.lower()],
                            title_single=LABELS[key.lower()],
                            obj_list=object_list[key],
                        )
                    }
                )

        body = self.render_group_view(obj_groups)
        if self.config.get("options.global.pin-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
