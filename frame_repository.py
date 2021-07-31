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
from frame_primary import PrimaryGrampsFrame
from frame_utils import TextLink

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# RepositoryGrampsFrame Class
#
# ------------------------------------------------------------------------
class RepositoryGrampsFrame(PrimaryGrampsFrame):
    """
    The RepositoryGrampsFrame exposes some of the basic facts about a
    Repository.
    """

    def __init__(
        self, grstate, context, repository, repo_ref=None, groups=None
    ):
        PrimaryGrampsFrame.__init__(
            self, grstate, context, repository, groups=groups
        )

        title = TextLink(
            repository.name,
            "Repository",
            repository.get_handle(),
            self.switch_object,
            bold=True,
        )
        self.title.pack_start(title, True, False, 0)

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
                text = "{}{}{}".format(text, comma, address.state)
                comma = ", "
            if address.country:
                text = "{}{}{}".format(text, comma, address.country)
            if address.postal:
                text = "{} {}".format(text, address.postal)
            if text:
                self.add_fact(self.make_label(text))
            if address.phone:
                self.add_fact(self.make_label(address.phone))

        if repo_ref:
            if self.option(context, "show-call-number"):
                if repo_ref.call_number:
                    text = "{}: {}".format(
                        _("Call number"), repo_ref.call_number
                    )
                    self.add_fact(self.make_label(text))

            if self.option(context, "show-media-type"):
                if repo_ref.media_type:
                    text = glocale.translation.sgettext(
                        repo_ref.media_type.xml_str()
                    )
                    if text:
                        text = "{}: {}".format(_("Media type"), text)
                    self.add_fact(self.make_label(text))

        if self.option(context, "show-repository-type"):
            if repository.type:
                text = glocale.translation.sgettext(repository.type.xml_str())
                if text:
                    label = self.make_label(text, left=False)
                    self.metadata.pack_start(label, False, False, 0)

        self.enable_drag()
        self.enable_drop()
        self.set_css_style()
