#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020      Nick Hall
# Copyright (C) 2020      Christian Schulze
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

import os
from gi.repository import Gtk
from gramps.gen.const import USER_PLUGINS

fname = os.path.join(USER_PLUGINS, "LinkedView", "icons")
icons = Gtk.IconTheme().get_default()
icons.append_search_path(fname)

register(
    VIEW,
    id="linked_view",
    name=_("Linked"),
    description=_("A browseable object view."),
    version="0.53",
    gramps_target_version="5.1",
    status=STABLE,
    fname="linked_view.py",
    authors=["The Gramps Project", "Christopher Horn"],
    authors_email=["http://gramps-project.org"],
    category=("Relationships", _("Relationships")),
    viewclass="LinkedView",
    stock_icon="gramps-relation-linked",
    order=END,
)
