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
ZoteroBibTex class
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import json

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.lib import (
    Source,
    SrcAttribute,
    SrcAttributeType,
    Citation,
    Note,
    NoteType,
    Person,
    Family,
    Event,
    Media,
)
from gramps.gen.lib.citationbase import CitationBase

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from .zotero_bibtex import ZoteroBibTex

_ = glocale.translation.sgettext

# -------------------------------------------------------------------------
#
# GrampsZotero class
#
# -------------------------------------------------------------------------
class GrampsZotero:
    """
    A simple class to partially interface Gramps with Zotero.
    """

    def __init__(self, db):
        self.db = db
        self.zotero = ZoteroBibTex()
        self.import_notes = False

    @property
    def online(self):
        """
        Check if service available.
        """
        return self.zotero.ping()

    def add_citation(
        self, primary_obj, secondary_obj=None, import_notes=False
    ):
        """
        Add citation to object selected by the Zotero picker.
        """
        if not self.zotero.ping():
            return None
        self.import_notes = import_notes
        zcitation, zsource, znotes = self.zotero.get_pick_data()
        if not zcitation:
            return None
        gsource = self.get_gramps_source(zsource)
        if not gsource:
            gsource = self.create_gramps_source(zsource, znotes)
        else:
            gsource = self.update_gramps_source(gsource, zsource, znotes)
        gcitation = self.create_gramps_citation(gsource, zcitation)
        self.add_citation_to_object(gcitation, primary_obj, secondary_obj)
        return gcitation

    def get_gramps_source(self, zsource):
        """
        Search and return matching source if one found.
        """
        zkey = zsource["citation-key"]
        for handle in self.db.iter_source_handles():
            gsource = self.db.get_source_from_handle(handle)
            citekey_attribute = find_attribute(gsource, "Zotero-key")
            if citekey_attribute and citekey_attribute.get_value() == zkey:
                return gsource
        return None

    def create_gramps_source(self, zsource, znotes):
        """
        Create Gramps source to match Zotero one.
        """
        gsource = Source()
        return self.update_gramps_source(
            gsource, zsource, znotes, update=False
        )

    def update_gramps_source(self, gsource, zsource, znotes, update=True):
        """
        Update Gramps source in case Zotero one changed.
        """
        change = False
        if "title" in zsource and gsource.get_title() != zsource["title"]:
            gsource.set_title(zsource["title"])
            change = True
        if (
            "publisher" in zsource
            and gsource.get_publication_info() != zsource["publisher"]
        ):
            gsource.set_publication_info(zsource["publisher"])
            change = True
        author = construct_author_string(zsource)
        if author and gsource.get_author() != author:
            gsource.set_author(author)
            change = True
        if merge_attributes(gsource, zsource):
            change = True
        if change:
            if update:
                message = " ".join(
                    (
                        _("Updating"),
                        _("Source"),
                        gsource.get_gramps_id(),
                        _("from"),
                        _("Zotero"),
                        _("Source"),
                        zsource["citation-key"],
                    )
                )
                with DbTxn(message, self.db) as trans:
                    self.db.commit_source(gsource, trans)
            else:
                message = " ".join(
                    (
                        _("Creating"),
                        _("Source"),
                        _("for"),
                        _("Zotero"),
                        _("Source"),
                        zsource["citation-key"],
                    )
                )
                with DbTxn(message, self.db) as trans:
                    handle = self.db.add_source(gsource, trans)
                gsource = self.db.get_source_from_handle(handle)
        if znotes and self.import_notes:
            gsource = self.sync_zotero_notes(gsource, zsource, znotes)
        return gsource

    def sync_zotero_notes(self, gsource, zsource, znotes):
        """
        Create or update Gramps notes from Zotero notes for a Gramps source.
        This may overwrite notes with different data but we treat them as a
        group. If notes are deleted in Zotero we may overwrite notes on Gramps
        side but we never delete the stragglers. Should make this optional.
        """
        change = False
        add_list, update_list = self._extract_note_lists(gsource, znotes)
        if update_list:
            for (index, note) in enumerate(update_list):
                note, note_change = self.update_gramps_zotero_note(
                    note, zsource, znotes[index]
                )
                if note_change:
                    gsource.add_note(note.get_handle())
                    change = True
        if add_list:
            change = True
            for znote in add_list:
                note, change = self.create_gramps_zotero_note(zsource, znote)
                gsource.add_note(note.get_handle())
        if change:
            message = " ".join(
                (
                    _("Updated"),
                    _("Notes"),
                    _("for"),
                    _("Source"),
                    zsource["citation-key"],
                )
            )
            with DbTxn(message, self.db) as trans:
                self.db.commit_source(gsource, trans)
        return gsource

    def _extract_note_lists(self, gsource, znotes):
        """
        Extract lists of notes to add, update, or delete.
        """
        current_znotes = self.get_gramps_zotero_notes(gsource)
        update_list = current_znotes[: len(znotes)]
        add_list = znotes[len(current_znotes) :]
        return add_list, update_list

    def get_gramps_zotero_notes(self, gobject):
        """
        Get Zotero notes for a Gramps object.
        """
        notes = []
        for handle in gobject.get_note_list():
            note = self.db.get_note_from_handle(handle)
            if note.get_type().xml_str() == "Zotero Note":
                notes.append(note)
        return notes

    def create_gramps_zotero_note(self, zsource, znote):
        """
        Create new Gramps Zotero note.
        """
        gnote = Note()
        gnotetype = NoteType()
        gnotetype.set_from_xml_str("Zotero Note")
        gnote.set_type(gnotetype)
        return self.update_gramps_zotero_note(
            gnote, zsource, znote, update=False
        )

    def update_gramps_zotero_note(self, gnote, zsource, znote, update=True):
        """
        Update a Gramps Zotero note.
        """
        change = False
        if gnote.get() != znote:
            gnote.set(znote)
            change = True
        if change:
            if update:
                message = " ".join(
                    (
                        _("Updating"),
                        _("Note"),
                        gnote.get_gramps_id(),
                        _("from"),
                        _("Zotero"),
                        _("Note"),
                        _("for"),
                        _("Source"),
                        zsource["citation-key"],
                    )
                )
                with DbTxn(message, self.db) as trans:
                    self.db.commit_note(gnote, trans)
            else:
                message = " ".join(
                    (
                        _("Creating"),
                        _("Note"),
                        _("for"),
                        _("Zotero"),
                        _("Note"),
                        _("for"),
                        _("Source"),
                        zsource["citation-key"],
                    )
                )
                with DbTxn(message, self.db) as trans:
                    handle = self.db.add_note(gnote, trans)
                gnote = self.db.get_note_from_handle(handle)
        return gnote, change

    def create_gramps_citation(self, gsource, zcitation):
        """
        Create new citation in Gramps.
        """
        gcitation = Citation()
        gcitation.set_reference_handle(gsource.get_handle())
        location = ""
        if (
            "label" in zcitation
            and "locator" in zcitation
            and zcitation["locator"]
        ):
            location = " ".join(
                (zcitation["label"].capitalize(), zcitation["locator"])
            )
        gcitation.set_page(location)
        message = " ".join(
            (
                _("Creating"),
                _("Citation"),
                _("from"),
                _("Source"),
                gsource.get_gramps_id(),
            )
        )
        with DbTxn(message, self.db) as trans:
            handle = self.db.add_citation(gcitation, trans)
        gcitation = self.db.get_citation_from_handle(handle)
        return gcitation

    def add_citation_to_object(self, gcitation, primary_obj, secondary_obj):
        """
        Add citation to Gramps object.
        """
        if secondary_obj and isinstance(secondary_obj, CitationBase):
            secondary_obj.add_citation(gcitation.get_handle())
        elif primary_obj and isinstance(primary_obj, CitationBase):
            primary_obj.add_citation(gcitation.get_handle())
        if isinstance(primary_obj, Person):
            obj_type = "Person"
            obj_lang = _("Person")
        elif isinstance(primary_obj, Event):
            obj_type = "Event"
            obj_lang = _("Event")
        elif isinstance(primary_obj, Family):
            obj_type = "Family"
            obj_lang = _("Family")
        elif isinstance(primary_obj, Media):
            obj_type = "Media"
            obj_lang = _("Media")
        commit = self.db.method("commit_%s", obj_type)
        message = " ".join(
            (
                _("Added"),
                _("Citation"),
                gcitation.get_gramps_id(),
                _("to"),
                obj_lang,
                primary_obj.get_gramps_id(),
            )
        )
        with DbTxn(message, self.db) as trans:
            commit(primary_obj, trans)

    def sync_zotero_sources(self):
        """
        Sync all Gramps sources extracted from Zotero updating as needed.
        """
        for handle in self.db.iter_source_handles():
            gsource = self.db.get_source_from_handle(handle)
            citekey = find_attribute(gsource, "Zotero-key")
            if citekey:
                zsource = self.zotero.get_source_data(citekey.get_value())
                if zsource:
                    znotes = self.zotero.get_note_data([citekey.get_value()])
                    self.update_gramps_source(gsource, zsource, znotes)


def construct_author_string(zsource):
    """
    Construct comma delimited author string.
    """
    author = ""
    comma = ""
    if "author" in zsource:
        for zauthor in zsource["author"]:
            name = ""
            if "given" in zauthor:
                name = zauthor["given"]
            if "family" in zauthor:
                name = " ".join((name, zauthor["family"]))
            if name:
                author = "".join((author, comma, name))
                comma = ", "
    return author


def find_attribute(obj, name):
    """
    Find an attribute for an object.
    """
    for attribute in obj.get_attribute_list():
        if attribute.get_type().xml_str() == name:
            return attribute
    return None


def merge_attributes(gsource, zsource):
    """
    Merge attributes from a Zotero source into the Gramps source.
    """
    change = False
    for zkey in zsource:
        if zkey in ["id", "author", "publisher", "title"]:
            continue
        if not zkey.isupper():
            gkey = zkey.capitalize()
        else:
            gkey = zkey
        if gkey == "Citation-key":
            gkey = "Zotero-key"
        gattribute = find_attribute(gsource, gkey)
        if not gattribute:
            gattribute = SrcAttribute()
            gtype = SrcAttributeType()
            gtype.set_from_xml_str(gkey)
            gattribute.set_type(gtype)
            gsource.add_attribute(gattribute)
        data = convert_string(zsource[zkey])
        if gattribute.get_value() != data:
            gattribute.set_value(data)
            change = True
    return change


def convert_string(data):
    """
    Convert data to string.
    """
    if isinstance(data, dict):
        data = json.dumps(data)
    elif isinstance(data, list):
        data = json.dumps(data)
    else:
        data = str(data)
    return data
