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
Card utility functions.
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
from html import escape

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import get_bookmarks, pack_icon, prepare_markup

_ = glocale.translation.sgettext


def get_tag_icon(tag, size=Gtk.IconSize.SMALL_TOOLBAR):
    """
    Return a colored tag icon.
    """
    icon = Gtk.Image()
    icon.set_from_icon_name("gramps-tag", size)
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


def load_metadata(widget, grstate, groptions, grobject, gramps_id=None):
    """
    Load the metadata section of the view for the given object.
    """
    obj = grobject.obj
    obj_type = grobject.obj_type
    config = grstate.config
    if config.get("display.use-smaller-icons"):
        icon_size = Gtk.IconSize.SMALL_TOOLBAR
    else:
        icon_size = Gtk.IconSize.LARGE_TOOLBAR

    if "Ref" in obj_type and groptions.ref_mode == 1:
        widget.set_halign(Gtk.Align.START)
        add_privacy_indicator(widget, config, obj, icon_size)
        pack_icon(widget, "stock_link", size=icon_size)

        if grobject.is_primary:
            add_gramps_id(widget, config, obj.gramps_id)
        elif gramps_id:
            add_gramps_id(widget, config, gramps_id)
    else:
        if grobject.is_primary:
            add_gramps_id(widget, config, obj.gramps_id)
        elif gramps_id:
            add_gramps_id(widget, config, gramps_id)

        if grobject.has_handle and config.get("indicator.bookmarks"):
            add_bookmark_indicator(
                widget, obj, obj_type, grstate.dbstate.db, icon_size
            )
        elif "Ref" in obj_type:
            pack_icon(widget, "stock_link", size=icon_size)

        add_privacy_indicator(widget, config, obj, icon_size)

        if obj_type == "Person" and config.get("indicator.home-person"):
            default = grstate.dbstate.db.get_default_person()
            if default and default.handle == obj.handle:
                pack_icon(
                    widget, "go-home", size=icon_size, tooltip=_("Home Person")
                )


def add_gramps_id(widget, config, gramps_id):
    """
    Add the gramps id if needed.
    """
    if config.get("indicator.gramps-ids"):
        scheme = global_config.get("colors.scheme")
        markup = prepare_markup(config, scheme=scheme)
        text = markup.format(escape(gramps_id))
        widget.pack_end(
            Gtk.Label(use_markup=True, label=text), False, False, 0
        )


def add_bookmark_indicator(widget, obj, obj_type, db, icon_size):
    """
    Add the bookmark indicator if needed.
    """
    handle = obj.handle
    for bookmark in get_bookmarks(db, obj_type).get():
        if bookmark == handle:
            pack_icon(
                widget,
                "gramps-bookmark",
                size=icon_size,
                tooltip=_("Bookmarked"),
            )
            break


def add_privacy_indicator(widget, config, obj, size):
    """
    Add privacy mode indicator if needed.
    """
    mode = config.get("indicator.privacy")
    if mode:
        if obj.private:
            if mode in [1, 3]:
                pack_icon(
                    widget, "gramps-lock", size=size, tooltip=_("Private")
                )
        else:
            if mode in [2, 3]:
                pack_icon(
                    widget, "gramps-unlock", size=size, tooltip=_("Public")
                )
