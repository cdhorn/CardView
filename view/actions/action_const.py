#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015-2016  Nick Hall
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
Action handler related constants
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gui.editors import (
    EditAddress,
    EditAttribute,
    EditCitation,
    EditEvent,
    EditFamily,
    EditLdsOrd,
    EditMedia,
    EditName,
    EditNote,
    EditPerson,
    EditPlace,
    EditRepository,
    EditSource,
    EditUrl,
)

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
_ = glocale.translation.sgettext


RECIPROCAL_ASSOCIATIONS = {
    _("Godfather"): _("Godchild"),
    _("Godmother"): _("Godchild"),
    _("Godparent"): _("Godchild"),
    _("Godchild"): _("Godparent"),
    _("Landlord"): _("Tenant"),
    _("Tenant"): _("Landlord"),
    _("DNA"): _("DNA"),
    _("cm"): _("cm"),
    _("Best Man"): _("Groom"),
    _("Maid of Honor"): _("Bride"),
    _("Friend"): _("Friend"),
    _("Employer"): _("Employee"),
    _("Employee"): _("Employer"),
    _("Lawyer"): _("Client"),
    _("Doctor"): _("Patient"),
    _("Patient"): _("Doctor"),
    _("Teacher"): _("Student"),
    _("Student"): _("Teacher"),
}

GRAMPS_EDITORS = {
    "Address": EditAddress,
    "Attribute": EditAttribute,
    "Citation": EditCitation,
    "Event": EditEvent,
    "Family": EditFamily,
    "LdsOrd": EditLdsOrd,
    "Media": EditMedia,
    "Name": EditName,
    "Note": EditNote,
    "Person": EditPerson,
    "Place": EditPlace,
    "Repository": EditRepository,
    "Source": EditSource,
    "Url": EditUrl,
}
