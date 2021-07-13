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
from gramps.gen.db import DbTxn


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_citation import CitationGrampsFrame
from frame_list import GrampsFrameList
from frame_utils import get_gramps_object_type

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


# ------------------------------------------------------------------------
#
# SourcesGrampsFrameGroup class
#
# ------------------------------------------------------------------------
class SourcesGrampsFrameGroup(GrampsFrameList):
    """
    The SourcesGrampsFrameGroup class provides a container for managing all
    of the cited sources for a given primary Gramps object.
    """

    def __init__(self, dbstate, uistate, router, obj, space, config):
        GrampsFrameList.__init__(self, dbstate, uistate, space, config, router=router)
        self.obj = obj
        self.obj_type, discard1, discard2 = get_gramps_object_type(obj)

        groups = {
            "data": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "metadata": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
            "image": Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL),
        }
        citation_list = self.collect_citations()
        
        if citation_list:
            if self.option("citation", "sort-by-date"):
                citation_list.sort(key=lambda x: x[0].get_date_object().get_sort_value())

            for citation, references, ref_type, ref_desc in citation_list:
                frame = CitationGrampsFrame(
                    self.dbstate,
                    self.uistate,
                    citation,
                    self.space,
                    self.config,
                    self.router,
                    groups=groups,
                    references=references,
                    ref_type=ref_type,
                    ref_desc=ref_desc
                )
                self.add_frame(frame)
        self.show_all()

    def save_new_object(self, handle, insert_row):
        """
        Add new citation to the list.
        """
        citation = self.dbstate.db.get_citation_from_handle()
        action = "{} {} {} {}".format(
            _("Added Citation"),
            citation.get_gramps_id(),
            _("to"),
            self.obj.get_gramps_id()
        )
        commit_method = self.dbstate.db.method("commit_%s", self.obj_type)
        with DbTxn(action, self.dbstate.db) as trans:
            if self.obj.add_citation(handle):
                commit_method(self.obj, trans)
        
    def collect_citations(self):
        """
        Helper to collect the citation data for the current object.
        """
        citation_list = []
        self.extract_citations(0, self.obj_type, citation_list, None, [self.obj])
        
        if self.option("citation", "include-indirect"):
            if self.obj_type == "Person":
                self.extract_citations(1, _("Primary Name"), citation_list, None, [self.obj.primary_name])
                self.extract_citations(1, _("Media"), citation_list, self.obj.get_media_list)
                self.extract_citations(1, _("Alternate Name"), citation_list, self.obj.get_alternate_names)
                self.extract_citations(1, _("Address"), citation_list, self.obj.get_address_list)
                self.extract_citations(1, _("Attribute"), citation_list, self.obj.get_attribute_list)
                self.extract_citations(1, _("LDS Event"), citation_list, self.obj.get_lds_ord_list)
                self.extract_citations(1, _("Association"), citation_list, self.obj.get_person_ref_list)
                self.extract_citations(1, _("Event"), citation_list, self.obj.get_event_ref_list)
                
        if self.option("citation", "include-family"):
            for family_handle in self.obj.get_family_handle_list():
                family = self.dbstate.db.get_family_from_handle(family_handle)
                self.extract_citations(0, "Family", citation_list, None, [family])
                if self.option("citation", "include-family-indirect"):
                    self.extract_citations(1, _("Family Media"), citation_list, family.get_media_list)
                    self.extract_citations(1, _("Family Attribute"), citation_list, family.get_attribute_list)
                    self.extract_citations(1, _("Family LDS Event"), citation_list, family.get_lds_ord_list)
                    self.extract_citations(1, _("Family Child"), citation_list, family.get_child_ref_list)
                    self.extract_citations(1, _("Family Event"), citation_list, family.get_event_ref_list)

        if self.option("citation", "include-parent-family"):
            if self.obj_type == "Person":
                for family_handle in self.obj.get_parent_family_handle_list():
                    family = self.dbstate.db.get_family_from_handle(family_handle)
                    for child_ref in family.get_child_ref_list():
                        if child_ref.ref == self.obj.get_handle():
                            for handle in child_ref.get_citation_list():
                                citation = self.dbstate.db.get_citation_from_handle(handle)
                                citation_list.append((citation, [child_ref], 1, _("Parent Family Child")))
        return citation_list

    def extract_citations(self, ref_type, ref_desc, citation_list, query_method=None, obj_list=[]):
        """
        Helper to extract a set of citations from an object.
        """
        if query_method:
            data = query_method()
        else:
            data = obj_list
        for item in data:
            if hasattr(item, "citation_list"):
                for handle in item.get_citation_list():
                    citation = self.dbstate.db.get_citation_from_handle(handle)
                    citation_list.append((citation, [item], ref_type, ref_desc))
