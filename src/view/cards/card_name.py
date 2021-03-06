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
NameCard
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext
from ..common.common_strings import MISSING_ORIGIN
from .card_secondary import SecondaryCard

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# NameCard Class
#
# ------------------------------------------------------------------------
class NameCard(SecondaryCard):
    """
    The NameCard exposes some of the basic facts about a Name.
    """

    def __init__(self, grstate, groptions, obj, name):
        SecondaryCard.__init__(self, grstate, groptions, obj, name)
        self.__add_name_title(obj, name)
        self.__add_name_given(name)
        self.__add_name_call(name)
        self.__add_name_nick(name)
        self.__add_name_origin_surnames(name)
        self.__add_name_family_nick(name)
        self.__add_name_date(name)
        self.show_all()
        self.enable_drag()
        self.enable_drop(
            self.eventbox, self.dnd_drop_targets, self.drag_data_received
        )
        self.set_css_style()

    def __add_name_title(self, obj, name):
        """
        Add title.
        """
        name_type = get_name_type(name)
        if obj.primary_name.serialize() == name.serialize():
            title = "%s: %s" % (_("Primary"), name_type)
        else:
            title = "%s: %s" % (_("Alternate"), name_type)
        label = self.get_link(
            title, "Person", obj.handle, callback=self.switch_name_page
        )
        self.widgets["title"].pack_start(label, False, False, 0)

    def __add_name_given(self, name):
        """
        Add given name with title if there is one.
        """
        given_name = name.get_regular_name()
        if name.title:
            given_name = "%s %s" % (name.title, given_name)
        self.add_fact(
            self.get_label(given_name), label=self.get_label(_("Given"))
        )

    def __add_name_call(self, name):
        """
        Add call name if there is one.
        """
        if name.call:
            self.add_fact(
                self.get_label(name.call),
                label=self.get_label(_("Call Name")),
            )

    def __add_name_nick(self, name):
        """
        Add nick name if there is one.
        """
        if name.nick:
            self.add_fact(
                self.get_label(name.nick),
                label=self.get_label(_("Nick Name")),
            )

    def __add_name_origin_surnames(self, name):
        """
        Add surnames with origin.
        """
        origin_type = ""
        for surname in name.get_surname_list():
            origin_type = get_origin_type(surname)
            prefix = ""
            if surname.get_prefix():
                prefix = "%s " % surname.get_prefix()
            connector = ""
            if surname.get_connector():
                connector = " %s" % surname.get_connector()

            text = "".join((prefix, surname.get_surname(), connector)).strip()
            if text:
                self.add_fact(
                    self.get_label(text), label=self.get_label(origin_type)
                )

    def __add_name_family_nick(self, name):
        """
        Add family_nick name if there is one.
        """
        if name.famnick:
            self.add_fact(
                self.get_label(name.famnick),
                label=self.get_label(_("Family Nick Name")),
            )

    def __add_name_date(self, name):
        """
        Add name date.
        """
        name_date = name.get_date_object()
        if name_date:
            text = glocale.date_displayer.display(name_date)
            if text:
                self.add_fact(
                    self.get_label(text), label=self.get_label(_("Date"))
                )
            if self.groptions.age_base and (
                self.groptions.context in ["timeline"]
                or self.grstate.config.get("group.name.show-age")
            ):
                self.load_age(self.groptions.age_base, name_date)

    def switch_name_page(self, *_dummy_obj):
        """
        Initiate switch to name page.
        """
        grcontext = GrampsContext(self.primary, None, self.secondary)
        return self.grstate.load_page(grcontext.pickled)


def get_name_type(name):
    """
    Return name type.
    """
    if name.get_type():
        return glocale.translation.sgettext(name.get_type().xml_str())
    return _("Unknown")


def get_origin_type(surname):
    """
    Return origin type.
    """
    if surname.get_origintype():
        origin_type = str(surname.get_origintype())
    if not origin_type:
        origin_type = MISSING_ORIGIN
    return origin_type
