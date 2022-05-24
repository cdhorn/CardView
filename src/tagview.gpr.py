# encoding:utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 Benny Malengier
# Copyright (C) 2009 Douglas S. Blank
# Copyright (C) 2009 Nick Hall
# Copyright (C) 2011 Tim G L Lyons
# Copyright (C) 2022 Christopher Horn
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
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

MODULE_VERSION = "5.1"

# ------------------------------------------------------------------------
#
# default views of Gramps
#
# ------------------------------------------------------------------------

register(
    VIEW,
    id="tagview",
    name=_("Tags"),
    description=_("The view showing all the tags"),
    version="0.93",
    gramps_target_version=MODULE_VERSION,
    status=STABLE,
    fname="tagview.py",
    authors=["The Gramps project"],
    authors_email=["http://gramps-project.org"],
    category=("Tags", _("Tags")),
    viewclass="TagView",
    order=START,
)
