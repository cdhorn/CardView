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
RepositoryGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_utils import TextLink
from .frame_reference import ReferenceGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoryGrampsFrame Class
#
# ------------------------------------------------------------------------
class RepositoryGrampsFrame(ReferenceGrampsFrame):
    """
    The RepositoryGrampsFrame exposes some of the basic facts about a
    Repository.
    """

    def __init__(self, grstate, groptions, repository, reference_tuple=None):
        ReferenceGrampsFrame.__init__(
            self,
            grstate,
            groptions,
            repository,
            reference_tuple=reference_tuple,
        )

        title = TextLink(
            repository.name,
            "Repository",
            repository.get_handle(),
            self.switch_object,
            bold=True,
        )
        self.widgets["title"].pack_start(title, True, False, 0)

        if repository.get_address_list():
            address = repository.get_address_list()[0]
            if address.street:
                self.add_fact(self.make_label(address.street))
            text = ""
            comma = ""
            if address.city:
                text = address.city
                comma = ", "
            if address.state:
                text = "".join((text, comma, address.state))
                comma = ", "
            if address.country:
                text = "".join((text, comma, address.country))
            if address.postal:
                text = " ".join((text, address.postal))
            if text:
                self.add_fact(self.make_label(text))
            if address.phone:
                self.add_fact(self.make_label(address.phone))

        if self.get_option("show-repository-type"):
            if repository.get_type():
                label = self.make_label(str(repository.get_type()), left=False)
                self.widgets["attributes"].add_fact(label)

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()
