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
LDSOrdinanceGrampsFrame
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.db import family_name

# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from ..common.common_classes import GrampsContext
from ..common.common_utils import TextLink, get_person_color_css
from .frame_secondary import SecondaryGrampsFrame

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# LDSOrdinanceGrampsFrame class
#
# ------------------------------------------------------------------------
class LDSOrdinanceGrampsFrame(SecondaryGrampsFrame):
    """
    The LDSOrdinanceGrampsFrame exposes the basic facts about an Ordinance.
    """

    def __init__(self, grstate, groptions, obj, ordinance):
        SecondaryGrampsFrame.__init__(self, grstate, groptions, obj, ordinance)

        title = ": ".join((_("LDS"), ordinance.type2str()))
        label = TextLink(
            title,
            self.primary.obj,
            self.primary.obj.get_handle(),
            self.switch_ordinance_page,
        )
        self.widgets["title"].pack_start(label, False, False, 0)

        if ordinance.get_date_object():
            date = glocale.date_displayer.display(ordinance.get_date_object())
            if date:
                self.add_fact(self.make_label(date))

            if groptions.age_base:
                if groptions.context in ["timeline"]:
                    self.load_age(
                        groptions.age_base, ordinance.get_date_object()
                    )
                elif self.grstate.config.get("options.group.ldsord.show-age"):
                    self.load_age(
                        groptions.age_base, ordinance.get_date_object()
                    )

        text = place_displayer.display_event(grstate.dbstate.db, ordinance)
        if text:
            place = TextLink(
                text,
                "Place",
                ordinance.place,
                self.switch_object,
                hexpand=False,
                bold=False,
                markup=self.markup,
            )
            self.add_fact(place)

        if ordinance.get_family_handle():
            family = self.grstate.fetch(
                "Family", ordinance.get_family_handle()
            )
            text = family_name(family, self.grstate.dbstate.db)
            self.add_fact(self.make_label(": ".join((_("Family"), text))))

        if ordinance.get_temple():
            temple = ": ".join((_("Temple"), ordinance.get_temple()))
            self.add_fact(self.make_label(temple))

        if ordinance.get_status():
            status = ": ".join((_("Status"), ordinance.status2str()))
            self.add_fact(self.make_label(status))

        self.show_all()
        self.enable_drop()
        self.set_css_style()

    def switch_ordinance_page(self, *_dummy_obj):
        """
        Initiate switch to ordinance page.
        """
        page_context = GrampsContext(
            self.primary.obj, None, self.secondary.obj
        )
        return self.grstate.load_page(page_context.pickled)

    def get_color_css(self):
        """
        Determine color scheme to be used if available."
        """
        if self.grstate.config.get("options.global.use-color-scheme"):
            if self.primary.obj_type == "Person":
                living = probably_alive(
                    self.primary.obj, self.grstate.dbstate.db
                )
                return get_person_color_css(
                    self.primary.obj,
                    living=living,
                )
        return ""
