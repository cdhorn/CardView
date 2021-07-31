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
# Plugin modules
#
# ------------------------------------------------------------------------
from .frame_primary import PrimaryGrampsFrame
from .frame_utils import TextLink


# ------------------------------------------------------------------------
#
# SourceGrampsFrame Class
#
# ------------------------------------------------------------------------
class SourceGrampsFrame(PrimaryGrampsFrame):
    """
    The SourceGrampsFrame exposes some of the basic facts about a Source.
    """

    def __init__(self, grstate, context, source, groups=None):
        PrimaryGrampsFrame.__init__(
            self, grstate, context, source, groups=groups
        )

        title = TextLink(
            source.title,
            "Source",
            source.get_handle(),
            self.switch_object,
            bold=True,
        )
        self.title.pack_start(title, True, False, 0)

        if source.get_author():
            self.add_fact(self.make_label(source.get_author()))

        if source.get_publication_info():
            self.add_fact(self.make_label(source.get_publication_info()))

        if source.get_abbreviation():
            self.add_fact(self.make_label(source.get_abbreviation()))

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()
