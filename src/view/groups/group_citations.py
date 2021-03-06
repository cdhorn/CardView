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
CitationsCardGroup
"""

# ------------------------------------------------------------------------
#
# Gramps Modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib.citationbase import CitationBase

# ------------------------------------------------------------------------
#
# Plugin Modules
#
# ------------------------------------------------------------------------
from ..cards import CitationCard
from .group_list import CardGroupList

_ = glocale.translation.sgettext


# ------------------------------------------------------------------------
#
# CitationsCardGroup Class
#
# ------------------------------------------------------------------------
class CitationsCardGroup(CardGroupList):
    """
    The CitationsCardGroup class provides a container for viewing and
    managing all of the citations associated with a primary Gramps object.
    """

    def __init__(self, grstate, groptions, obj):
        CardGroupList.__init__(
            self, grstate, groptions, obj, enable_drop=False
        )
        if self.group_base.is_primary:
            groptions.set_backlink(
                (self.group_base.obj_type, self.group_base.obj.handle)
            )
        self.maximum = grstate.config.get("group.citation.max-per-group")
        citation_list = self.collect_citations()
        if citation_list:
            if self.get_option("sort-by-date"):
                citation_list.sort(
                    key=lambda x: x[0].get_date_object().sortval
                )

            for citation, references, ref_type, ref_desc in citation_list:
                reference = (references, ref_type, ref_desc)
                card = CitationCard(
                    grstate, groptions, citation, reference=reference
                )
                self.add_card(card)
        self.show_all()

    def save_new_object(self, handle, insert_row):
        """
        Add new citation to the list.
        """
        citation = self.fetch("Citation", handle)
        message = " ".join(
            (
                _("Added"),
                _("Citation"),
                citation.gramps_id,
                _("to"),
                self.group_base.obj.gramps_id,
            )
        )
        self.group_base.obj.add_citation(handle)
        self.group_base.commit(self.grstate, message)

    def collect_citations(self):
        """
        Helper to collect the citation data for the current object.
        """
        group_base_obj = self.group_base.obj
        group_base_obj_type = self.group_base.obj_type
        citation_list = []
        self.extract_citations(
            0,
            group_base_obj_type,
            citation_list,
            None,
            [group_base_obj],
        )

        if group_base_obj_type == "Person":
            if self.get_option("include-indirect"):
                self.extract_citations(
                    1,
                    _("Primary Name"),
                    citation_list,
                    None,
                    [group_base_obj.primary_name],
                )
                self.extract_citations(
                    1,
                    _("Media"),
                    citation_list,
                    group_base_obj.get_media_list,
                )
                self.extract_citations(
                    1,
                    _("Alternate Name"),
                    citation_list,
                    group_base_obj.get_alternate_names,
                )
                self.extract_citations(
                    1,
                    _("Address"),
                    citation_list,
                    group_base_obj.get_address_list,
                )
                self.extract_citations(
                    1,
                    _("Attribute"),
                    citation_list,
                    group_base_obj.get_attribute_list,
                )
                self.extract_citations(
                    1,
                    _("LDS Event"),
                    citation_list,
                    group_base_obj.get_lds_ord_list,
                )
                self.extract_citations(
                    1,
                    _("Association"),
                    citation_list,
                    group_base_obj.get_person_ref_list,
                )
                self.extract_citations(
                    1,
                    _("Event"),
                    citation_list,
                    group_base_obj.get_event_ref_list,
                )

            if self.get_option("include-family"):
                for family_handle in group_base_obj.family_list:
                    family = self.fetch("Family", family_handle)
                    self.extract_citations(
                        0, "Family", citation_list, None, [family]
                    )
                    if self.get_option("include-family-indirect"):
                        self.extract_family_citations(citation_list, family)

            if self.get_option("include-parent-family"):
                for family_handle in group_base_obj.parent_family_list:
                    family = self.fetch("Family", family_handle)
                    for child_ref in family.child_ref_list:
                        if child_ref.ref == group_base_obj.handle:
                            for handle in child_ref.citation_list:
                                citation = self.fetch("Citation", handle)
                                citation_list.append(
                                    (
                                        citation,
                                        [child_ref],
                                        1,
                                        _("Parent Family Child"),
                                    )
                                )

        if group_base_obj_type == "Family" and self.get_option(
            "include-indirect"
        ):
            self.extract_family_citations(citation_list, group_base_obj)

        if group_base_obj_type == "Source":
            for (
                obj_type,
                obj_handle,
            ) in self.grstate.dbstate.db.find_backlink_handles(
                group_base_obj.handle, ["Citation"]
            ):
                citation = self.fetch("Citation", obj_handle)
                citation_list.append((citation, [group_base_obj], 0, obj_type))
                if len(citation_list) >= self.maximum:
                    break

        return citation_list

    def extract_citations(
        self,
        ref_type,
        ref_desc,
        citation_list,
        query_method=None,
        obj_list=None,
    ):
        """
        Helper to extract a set of citations from an object.
        """

        if query_method:
            data = query_method()
        else:
            data = obj_list or []
        for item in data:
            if isinstance(item, CitationBase):
                for handle in item.citation_list:
                    citation = self.fetch("Citation", handle)
                    citation_list.append(
                        (citation, [item], ref_type, ref_desc)
                    )
                    if len(citation_list) >= self.maximum:
                        break

    def extract_family_citations(self, citation_list, family):
        """
        Helper to extract indirect citations for a family.
        """
        self.extract_citations(
            1, _("Family Media"), citation_list, family.get_media_list
        )
        self.extract_citations(
            1, _("Family Attribute"), citation_list, family.get_attribute_list
        )
        self.extract_citations(
            1, _("Family LDS Event"), citation_list, family.get_lds_ord_list
        )
        self.extract_citations(
            1, _("Family Child"), citation_list, family.get_child_ref_list
        )
        self.extract_citations(
            1, _("Family Event"), citation_list, family.get_event_ref_list
        )
