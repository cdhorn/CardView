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
Media Profile Page
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
from ..frames.frame_classes import GrampsState, GrampsOptions
from ..frames.frame_image import ImageGrampsFrame
from ..groups.group_utils import (
    get_attributes_group,
    get_citations_group,
    get_notes_group,
    get_references_group,
    get_urls_group,
)
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class MediaProfilePage(BaseProfilePage):
    """
    Provides the media item profile page view with information about the media.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)

    def obj_type(self):
        return "Media"

    def page_type(self):
        return "Media"

    def define_actions(self, view):
        return

    def enable_actions(self, uimanager, person):
        return

    def disable_actions(self, uimanager):
        return

    def render_page(self, header, vbox, media, secondary=None):
        list(map(header.remove, header.get_children()))
        list(map(vbox.remove, vbox.get_children()))
        if not media:
            return

        grstate = GrampsState(
            self.dbstate,
            self.uistate,
            self.callbacks,
            self.config,
            self.page_type().lower(),
        )
        groptions = GrampsOptions("options.active.media")
        self.active_profile = ImageGrampsFrame(grstate, groptions, media)

        groups = self.config.get("options.page.media.layout.groups").split(",")
        obj_groups = {}

        if "citation" in groups:
            obj_groups.update({"citation": get_citations_group(grstate, media)})
        if "attribute" in groups:
            obj_groups.update(
                {"attribute": get_attributes_group(grstate, media)}
            )
        if "url" in groups:
            obj_groups.update({"url": get_urls_group(grstate, media)})
        if "note" in groups:
            obj_groups.update({"note": get_notes_group(grstate, media)})
        if "reference" in groups:
            obj_groups.update(
                {"reference": get_references_group(grstate, media)}
            )

        body = self.render_group_view(obj_groups)
        if self.config.get("options.global.pin-header"):
            header.pack_start(self.active_profile, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(self.active_profile, False, False, 0)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
