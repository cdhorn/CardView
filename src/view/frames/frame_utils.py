#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2021-2022  Christopher Horn
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
Frame utility functions.
"""

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


def get_tag_icon(tag):
    """
    Return a colored tag icon.
    """
    icon = Gtk.Image()
    icon.set_from_icon_name("gramps-tag", Gtk.IconSize.BUTTON)
    css = "".join(
        (
            ".image { margin: 0px; padding: 0px; background-image: none; ",
            "background-color: ",
            tag.color[:7],
            "; }",
        )
    )
    css = css.encode("utf-8")
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    context = icon.get_style_context()
    context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    context.add_class("image")
    return icon
