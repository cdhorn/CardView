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
Citation Profile Page
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

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
from ..frames.frame_citation import CitationGrampsFrame
from ..frames.frame_source import SourceGrampsFrame
from .page_base import BaseProfilePage

_ = glocale.translation.sgettext


class CitationProfilePage(BaseProfilePage):
    """
    Provides the citation profile page view with information about the citation.
    """

    def __init__(self, dbstate, uistate, config, callbacks):
        BaseProfilePage.__init__(self, dbstate, uistate, config, callbacks)
        self.active_profile = None

    @property
    def obj_type(self):
        return "Citation"

    @property
    def page_type(self):
        return "Citation"

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

        citation = context.primary_obj.obj

        groptions = GrampsOptions("options.active.citation")
        self.active_profile = CitationGrampsFrame(
            self.grstate, groptions, citation
        )

        source = self.grstate.dbstate.db.get_source_from_handle(
            self.active_profile.primary.obj.source_handle
        )
        groptions = GrampsOptions("options.active.source")
        source_frame = SourceGrampsFrame(self.grstate, groptions, source)

        groups = self.config.get("options.page.citation.layout.groups").split(
            ","
        )
        obj_groups = self.get_object_groups(groups, citation)
        body = self.render_group_view(obj_groups)

        hbox = Gtk.VBox()
        hbox.pack_start(source_frame, True, True, 0)
        hbox.pack_start(self.active_profile, True, True, 0)
        if self.config.get("options.global.pin-header"):
            header.pack_start(hbox, False, False, 0)
            header.show_all()
        else:
            vbox.pack_start(hbox, False, False, 0)
        self.add_media_bar(vbox, citation)
        vbox.pack_start(body, False, False, 0)
        vbox.show_all()
        return
