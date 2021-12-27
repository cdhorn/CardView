#
# Gramps - a GTK+/GNOME based genealogy program
#
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
NameGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.alive import probably_alive

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext
from ..common.common_utils import get_person_color_css
from .frame_secondary import SecondaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# NameGrampsFrame class
#
# ------------------------------------------------------------------------
class NameGrampsFrame(SecondaryGrampsFrame):
    """
    The NameGrampsFrame exposes some of the basic facts about a Name.
    """

    def __init__(self, grstate, groptions, obj, name):
        SecondaryGrampsFrame.__init__(self, grstate, groptions, obj, name)
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
            title = ": ".join((_("Primary"), name_type))
        else:
            title = ": ".join((_("Alternate"), name_type))
        label = self.get_link(
            title, "Person", obj.get_handle(), callback=self.switch_name_page
        )
        self.widgets["title"].pack_start(label, False, False, 0)

    def __add_name_given(self, name):
        """
        Add given name with title if there is one.
        """
        given_name = name.get_regular_name()
        if name.get_title():
            given_name = " ".join((name.get_title(), given_name))
        self.add_fact(
            self.get_label(given_name), label=self.get_label(_("Given"))
        )

    def __add_name_call(self, name):
        """
        Add call name if there is one.
        """
        if name.get_call_name():
            self.add_fact(
                self.get_label(name.get_call_name()),
                label=self.get_label(_("Call Name")),
            )

    def __add_name_nick(self, name):
        """
        Add nick name if there is one.
        """
        if name.get_nick_name():
            self.add_fact(
                self.get_label(name.get_nick_name()),
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
                prefix = "".join((surname.get_prefix(), " "))
            connector = ""
            if surname.get_connector():
                connector = "".join((" ", surname.get_connector()))

            text = "".join((prefix, surname.get_surname(), connector)).strip()
            if text:
                self.add_fact(
                    self.get_label(text), label=self.get_label(origin_type)
                )

    def __add_name_family_nick(self, name):
        """
        Add family_nick name if there is one.
        """
        if name.get_family_nick_name():
            self.add_fact(
                self.get_label(name.get_family_nick_name()),
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
                or self.grstate.config.get("options.group.name.show-age")
            ):
                self.load_age(self.groptions.age_base, name_date)

    def switch_name_page(self, *_dummy_obj):
        """
        Initiate switch to name page.
        """
        grcontext = GrampsContext(self.primary, None, self.secondary)
        return self.grstate.load_page(grcontext.pickled)

    def edit_secondary_object(self, _dummy_var1=None):
        """
        Override default method to launch the name editor.
        """
        self.edit_name(None, self.secondary.obj)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if (
            self.grstate.config.get("options.global.display.use-color-scheme")
            and self.primary.obj_type == "Person"
        ):
            living = probably_alive(self.primary.obj, self.grstate.dbstate.db)
            return get_person_color_css(
                self.primary.obj,
                living=living,
            )
        return ""


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
        origin_type = "".join(("[", _("Missing Origin"), "]"))
    return origin_type
