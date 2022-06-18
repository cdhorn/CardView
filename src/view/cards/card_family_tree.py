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
FamilyTreeCard
"""

# ------------------------------------------------------------------------
#
# Python Modules
#
# ------------------------------------------------------------------------
from html import escape
import os

# ------------------------------------------------------------------------
#
# GTK Modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.const import GRAMPS_LOCALE
from gramps.gen.dbstate import DbState
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Note, NoteType
from gramps.gui.editors import EditNote

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from .card_generic import GenericCard
from .card_widgets import CardGrid
from ..common.common_strings import NONE
from ..common.common_utils import format_address, TextLink

_ = GRAMPS_LOCALE.translation.sgettext


# ------------------------------------------------------------------------
#
# FamilyTreeCard Class
#
# ------------------------------------------------------------------------
class FamilyTreeCard(GenericCard):
    """
    The FamilyTreeCard displays some information about the active tree.
    """

    def __init__(self, grstate, groptions):
        GenericCard.__init__(self, grstate, groptions, None)
        self.title = _("Family Tree Summary")
        self.build_layout()
        grstate.dbstate.db.connect("home-person-changed", self.load_layout)
        self.person_history = self.grstate.uistate.get_history("Person")
        self.person_history.connect("active-changed", self.load_layout)
        self.load_layout()
        self.set_css_style()

    def load_layout(self, *args):
        """
        Load the layout.
        """
        widgets = self.widgets
        if self.title:
            label = Gtk.Label(
                use_markup=True,
                label=self.title_markup.format(
                    "<b>%s</b>" % escape(self.title)
                ),
            )
            widgets["title"].pack_start(label, False, False, 0)

        facts = self.widgets["facts"]
        list(map(facts.remove, facts.get_children()))
        if not self.grstate.dbstate.is_open():
            self.add_fact(facts, _("None currently open"), _("Name"))
            return

        db = self.grstate.dbstate.db
        db_name, db_id, db_type, db_size = get_database_information(db)
        self.add_fact(facts, db_name, _("Name"))
        if db_type:
            db_id = "%s (%s)" % (db_id, db_type)
        self.add_fact(facts, db_id, _("Id"))
        if db_size:
            self.add_fact(facts, db_size, _("Size"))

        home_person = db.get_default_person()
        if home_person:
            home_person_name = name_displayer.display(home_person)
            facts.add_fact(
                self.get_link(home_person_name, "Person", home_person.handle),
                label=self.get_label(_("Home Person")),
            )
        else:
            self.add_fact(facts, NONE, _("Home Person"))

        if self.person_history.present():
            active_person = db.get_person_from_handle(
                self.person_history.present()
            )
            active_person_name = name_displayer.display(active_person)
            facts.add_fact(
                self.get_link(
                    active_person_name, "Person", active_person.handle
                ),
                label=self.get_label(_("Active Person")),
            )
        else:
            self.add_fact(facts, NONE, _("Active Person"))

        facts = self.widgets["facts2"]
        list(map(facts.remove, facts.get_children()))
        facts.add_fact(self.get_label(""), self.get_label(_("Description")))
        db_note = self.get_database_description_note()
        if not db_note:
            db_description = _("[None found, right mouse click to add]")
        else:
            db_description = db_note.get()
        facts.add_fact(self.get_label(db_description))

        facts = self.widgets["facts3"]
        list(map(facts.remove, facts.get_children()))
        researcher = self.grstate.dbstate.db.get_researcher()
        self.add_fact(facts, researcher.name, _("Owner"))
        first = True
        for line in format_address(researcher):
            if first:
                self.add_fact(facts, line, _("Address"))
                first = False
            else:
                self.add_fact(facts, line, "")
        self.add_fact(facts, researcher.email, _("Email"))
        self.add_fact(facts, researcher.phone, _("Phone"))
        self.show_all()

    def build_layout(self):
        """
        Construct basic card layout.
        """
        widgets = self.widgets
        widgets["facts2"] = CardGrid()
        widgets["facts3"] = CardGrid()

        fact_block = Gtk.VBox()
        widgets["body"].pack_start(
            fact_block, expand=True, fill=True, padding=0
        )
        fact_block.pack_start(
            widgets["title"], expand=True, fill=True, padding=0
        )
        hbox = Gtk.HBox(vexpand=False)
        hbox.pack_start(widgets["facts"], expand=True, fill=True, padding=0)
        hbox.pack_start(widgets["facts2"], expand=True, fill=True, padding=0)
        hbox.pack_start(widgets["facts3"], expand=True, fill=True, padding=0)
        fact_block.pack_start(hbox, expand=True, fill=True, padding=0)

    def add_fact(self, facts, value, label):
        """
        Add none if not set.
        """
        if value:
            facts.add_fact(self.get_label(value), label=self.get_label(label))
        else:
            facts.add_fact(self.get_label(NONE), label=self.get_label(label))

    def get_database_description_note(self):
        """
        Find database description.
        """
        for note in self.grstate.dbstate.db.iter_notes():
            if str(note.get_type()) == "Database Description":
                return note
        return None

    def set_css_style(self):
        """
        Apply some simple styling to the frame of the current object.
        """
        border = self.grstate.config.get("display.border-width")
        color = self.get_color_css()
        css = "".join(
            (".frame { border-width: ", str(border), "px; ", color, " }")
        )
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = self.frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")

    def build_context_menu(self, _dummy_obj, event):
        """
        Launch database owner editor.
        """
        note = self.get_database_description_note()
        if not note:
            note = Note()
            note_type = NoteType("Database Description")
            note.set_type(note_type)
        try:
            EditNote(self.grstate.dbstate, self.grstate.uistate, [], note)
        except WindowActiveError:
            pass


def get_database_information(db):
    """
    Return the database information.
    """
    db_name = db.get_dbname()
    db_id = db.get_dbid()

    db_type = None
    dbstate = DbState()
    db_summary = CLIDbManager(dbstate).family_tree_summary(
        database_names=[db_name]
    )
    if db_summary:
        db_key = GRAMPS_LOCALE.translation.sgettext("Database")
        for key in db_summary[0]:
            if key == db_key:
                db_type = db_summary[0][key]

    db_file = os.path.join(db.get_save_path(), "sqlite.db")
    try:
        file_size = os.path.getsize(db_file)
        db_size = "%s MB" % str(int(file_size / 1048576))
    except OSError:
        db_size = ""

    return db_name, db_id, db_type, db_size
