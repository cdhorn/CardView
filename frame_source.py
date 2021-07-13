#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021      Christopher Horn
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
SourceGrampsFrame.
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import PlaceDisplay
from gramps.gen.lib import Citation


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_base import GrampsFrame
from frame_utils import _CONFIDENCE, get_confidence, get_confidence_color_css, TextLink


# ------------------------------------------------------------------------
#
# Internationalisation
#
# ------------------------------------------------------------------------

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

pd = PlaceDisplay()


# ------------------------------------------------------------------------
#
# SourceGrampsFrame Class
#
# ------------------------------------------------------------------------
class SourceGrampsFrame(GrampsFrame):
    """
    The SourceGrampsFrame exposes some of the basic facts about a Source.
    """

    def __init__(self, dbstate, uistate, source, context, space, config, router, groups=None, defaults=None):
        GrampsFrame.__init__(
            self, dbstate, uistate, router, space, config, source, context, groups=groups, defaults=defaults
        )
        self.source = source
        self.enable_drag()
        self.enable_drop()
        
        text = "<b>{}</b>".format(self.source.title.replace('&', '&amp;'))
        title = TextLink(text, "Source", self.source.get_handle(), self.switch_object)
        self.title.pack_start(title, True, False, 0)

        if self.source.get_author():
            author = self.make_label(self.source.get_author())
            self.add_fact(author)

        if self.source.get_publication_info():
            publisher = self.make_label(self.source.get_publication_info())
            self.add_fact(publisher)

        if self.source.get_abbreviation():
            abbreviation = self.make_label(self.source.get_abbreviation())
            self.add_fact(abbreviation)
        
        self.set_css_style()

