#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2022       Christopher Horn
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
Common strings for cards
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale


_ = glocale.translation.sgettext


REFERENCE = _("reference")
EDIT_REFERENCE = "%s %s" % (_("Edit"), REFERENCE)
DELETE_REFERENCE = "%s %s" % (_("Delete"), REFERENCE)
NONE_PROVIDED = "[%s]" % _("None Provided")
BACK_REFERENCE = "[%s]" % _("Back Reference")
RECIPROCAL = "[%s]" % _("Reciprocal")
MISSING = "[%s]" % _("Missing")
LATITUDE_LONGITUDE = "%s, %s" % (_("Latitude"), _("Longitude"))
MAKE_MEDIA_ACTIVE = "%s %s %s" % (_("Make"), _("media"), _("active"))
UNKNOWN = "[%s]" % _("Unknown")
UNTITLED = "[%s]" % _("Untitled")
NONE = "[%s]" % _("None")
UNAVAILABLE = "[%s]" % _("Unavailable")
MISSING_ORIGIN = "[%s]" % _("Missing Origin")
