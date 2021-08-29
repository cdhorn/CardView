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
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


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
from .frame_secondary import SecondaryGrampsFrame
from .frame_utils import get_person_color_css, TextLink

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

        if name.get_type():
            name_type = glocale.translation.sgettext(name.get_type().xml_str())
        else:
            name_type = _("Unknown")
        if obj.primary_name.serialize() == name.serialize():
            title = "{}: {}".format(_("Primary"), name_type)
        else:
            title = "{}: {}".format(_("Alternate"), name_type)
        label = TextLink(
            title, "Person", obj.get_handle(), self.switch_name_page
        )
        self.title.pack_start(label, False, False, 0)

        given_name = name.get_regular_name()
        if name.get_title():
            given_name = "{} {}".format(name.get_title(), given_name)
        self.add_fact(self.make_label(given_name))

        if name.get_call_name():
            call_name = "{} {}".format(_("Call Name:"), name.get_call_name())
            self.add_fact(self.make_label(call_name))

        if name.get_nick_name():
            nick_name = "{} {}".format(_("Nick Name:"), name.get_nick_name())
            self.add_fact(self.make_label(nick_name))

        origin_type = ""
        for surname in name.get_surname_list():
            if surname.get_origintype():
                origin_type = str(surname.get_origintype())
            if not origin_type:
                origin_type = "[{}]".format(_("Missing Origin"))

            prefix = ""
            if surname.get_prefix():
                prefix = "{} ".format(surname.get_prefix())

            connector = ""
            if surname.get_connector():
                connector = " {}".format(surname.get_connector())

            text = "{}{}{}".format(
                prefix, name.get_surname(), connector
            ).strip()
            if text:
                text = "{}: {}".format(origin_type, text)
                self.add_fact(self.make_label(text))

        if name.get_family_nick_name():
            nick_name = "{} {}".format(
                _("Family Nick Name:"), name.get_family_nick_name()
            )
            self.add_fact(self.make_label(nick_name))

        if name.get_date_object():
            text = glocale.date_displayer.display(name.get_date_object())
            if text:
                self.add_fact(self.make_label(text))

            if groptions.age_base:
                self.load_age(groptions.age_base, name.get_date_object())

        self.show_all()
        self.enable_drag()
        self.enable_drop()
        self.set_css_style()

    def switch_name_page(self, *_dummy_obj):
        """
        Initiate switch to name page.
        """
        self.switch_object(None, None, "Name", self.secondary.obj)

    def edit_secondary_object(self, _dummy_var1=None):
        """
        Override default method to launch the name editor.
        """
        self.edit_name(None, self.secondary.obj)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if not self.grstate.config.get("options.global.use-color-scheme"):
            return ""

        if self.primary.obj_type == "Person":
            living = probably_alive(self.primary.obj, self.grstate.dbstate.db)
            return get_person_color_css(
                self.primary.obj,
                living=living,
            )
