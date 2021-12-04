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
from ..common.common_const import GROUP_LABELS
from ..frames.frame_tag import TagGrampsFrame
from ..groups.group_utils import get_references_group
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class TagProfilePage(BaseProfilePage):
    """
    Provides the tag profile page view with information about the tagged
    objects.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
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
        return "Tag"

    def render_page(self, header, vbox, context):
        """
        Render the page contents.
        """
        if not context:
            return

        tag = context.primary_obj.obj

        groptions = GrampsOptions("options.active.tag")
        self.active_profile = TagGrampsFrame(self.grstate, groptions, tag)
        focal = self.wrap_focal_widget(self.active_profile)

        object_list = {}
        for (
            obj_type,
            obj_handle,
        ) in self.grstate.dbstate.db.find_backlink_handles(tag.get_handle()):
            if obj_type not in object_list:
                object_list.update({obj_type: []})
            object_list[obj_type].append((obj_type, obj_handle))

        obj_groups = {}
        if object_list:
            for key, value in object_list.items():
                groptions = GrampsOptions(
                    "options.group.{}".format(key.lower())
                )
                obj_groups.update(
                    {
                        key.lower(): get_references_group(
                            self.grstate,
                            None,
                            None,
                            groptions=groptions,
                            obj_list=value,
                        )
                    }
                )

        body = self.render_group_view(obj_groups)
        if self.config.get("options.global.pin-header"):
            header.pack_start(focal, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(focal, False, False, 0)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
