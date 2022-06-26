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
Statistics service labels
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


# Each gathered statistic has a key to identify it. The following maps are
# for looking up the translated label to describe it on a card or elsewhere.

PERSON_LABELS = {
    "total": _("Number of individuals"),
    "incomplete_names": _("With incomplete names"),
    "alternate_names": _("With alternate names"),
    "no_family_connection": _("Disconnected from a family"),
    "male_total": _("Males"),
    "male_living": _("Living males"),
    "no_birth": _("Missing birth"),
    "no_birth_date": _("Missing preferred birth date"),
    "no_birth_place": _("Missing preferred birth place"),
    "no_baptism": _("Missing baptism or christening"),
    "no_baptism_date": _("Missing baptism or christening date"),
    "no_baptism_place": _("Missing baptism or christening place"),
    "no_death": _("Missing death and not living"),
    "no_death_date": _("Missing preferred death date"),
    "no_death_place": _("Missing preferred death place"),
    "no_burial": _("Missing burial or cremation and not living"),
    "no_burial_date": _("Missing burial or cremation date"),
    "no_burial_place": _("Missing burial or cremation place"),
    "female_total": _("Females"),
    "female_living": _("Living females"),
    "unknown_total": _("Unknown genders"),
    "unknown_living": _("Living unknown genders"),
}


ASSOCIATION_LABELS = {
    "total": _("People with associations"),
    "refs": _("Total association references"),
    "types": _("Association types"),
}


PARTICIPANT_LABELS = {
    "total": _("Participants in events"),
    "refs": _("Total event participant references"),
    "person_roles": _("Individual participant roles"),
    "family_roles": _("Family participant roles"),
}


FAMILY_LABELS = {
    "total": _("Number of families"),
    "surname_total": _("Unique surnames"),
    "relations": _("Relationship types"),
    "missing_one": _("Missing one partner"),
    "missing_both": _("Missing both partners"),
    "no_events": _("Missing events"),
    "no_child": _("Childless"),
    "no_marriage_date": _("Missing marriage date"),
    "no_marriage_place": _("Missing marriage place"),
}


CHILD_LABELS = {
    "refs": _("Total child references"),
    "father_relations": _("Father relationships"),
    "mother_relations": _("Mother relationships"),
}


EVENT_LABELS = {
    "total": _("Number of events"),
    "no_date": _("Missing date"),
    "no_place": _("Missing place"),
    "no_description": _("Missing description"),
    "types": _("Event types"),
}


LDSORD_PERSON_LABELS = {
    "ldsord": _("Number of people with ordinances"),
    "ldsord_refs": _("Total person ordinances"),
    "no_date": _("Missing date"),
    "no_place": _("Missing place"),
    "no_temple": _("Missing temple"),
    "no_status": _("Missing status"),
    "no_family": _("Missing family"),
}


LDSORD_FAMILY_LABELS = {
    "ldsord": _("Number of families with ordinances"),
    "ldsord_refs": _("Total family ordinances"),
    "no_date": _("Missing date"),
    "no_place": _("Missing place"),
    "no_temple": _("Missing temple"),
    "no_status": _("Missing status"),
}


PLACE_LABELS = {
    "total": _("Number of places"),
    "no_name": _("Missing name"),
    "no_latitude": _("Missing latitude"),
    "no_longitude": _("Missing longitude"),
    "no_code": _("Missing place code"),
    "types": _("Place types"),
}


UNCITED_LABELS = {
    "names": _("Names of people"),
    "male": _("Males"),
    "female": _("Females"),
    "unknown": _("Unknown genders"),
    "preferred_births": _("Preferred births"),
    "preferred_deaths": _("Preferred deaths"),
    "family": _("Families"),
    "child": _("Children"),
    "association": _("Associations"),
    "event": _("Events"),
    "ldsord_person": _("Person ordinances"),
    "ldsord_family": _("Family ordinances"),
    "place": _("Places"),
    "media": _("Media"),
    "events": _("Events"),
}


PRIVATE_LABELS = {
    "male": _("Males"),
    "male_living_not": _("Living males not private"),
    "female": _("Females"),
    "female_living_not": _("Living females not private"),
    "unknown": _("Unknown genders"),
    "unknown_living_not": _("Living unknown genders not private"),
    "preferred_births": _("Preferred births"),
    "baptism": _("Baptisms and christenings"),
    "preferred_deaths": _("Preferred deaths"),
    "burial": _("Burials and cremations"),
    "names": _("Names of people"),
    "family": _("Families"),
    "marriage": _("Marriages"),
    "child": _("Children"),
    "association": _("Associations"),
    "event": _("Events"),
    "participant": _("Individual participants"),
    "family_participant": _("Family participants"),
    "ldsord_person": _("LDS person ordinances"),
    "ldsord_family": _("LDS family ordinances"),
    "place": _("Places"),
    "media": _("Media objects"),
    "citation": _("Citations"),
    "source": _("Sources"),
    "repository": _("Repositories"),
    "note": _("Notes"),
}


MEDIA_LABELS = {
    "total": _("Number of unique media items"),
    "size": _("Total size of media objects"),
    "no_file": _("Missing file"),
    "no_path": _("Missing path"),
    "no_description": _("Missing description"),
    "no_mime": _("Missing mime type"),
    "no_date": _("Missing date"),
    "person": _("People with media"),
    "person_refs": _("Total person media references"),
    "person_missing_region": _("Person media references missing region"),
    "family": _("Families with media"),
    "family_refs": _("Total family media references"),
    "event": _("Events with media"),
    "event_refs": _("Total event media references"),
    "place": _("Places with media"),
    "place_refs": _("Total place media references"),
    "source": _("Sources with media"),
    "source_refs": _("Total source media references"),
    "citation": _("Citations with media"),
    "citation_refs": _("Total citation media references"),
}


CITATION_LABELS = {
    "total": _("Number of citations"),
    "no_source": _("Missing source"),
    "no_page": _("Missing page"),
    "no_date": _("Missing date"),
    "confidence": _("Confidence level"),
    "very_low": _("Very low"),
    "low": _("Low"),
    "normal": _("Normal"),
    "high": _("High"),
    "very_high": _("Very high"),
}


SOURCE_LABELS = {
    "total": _("Number of sources"),
    "no_title": _("Missing title"),
    "no_author": _("Missing author"),
    "no_pubinfo": _("Missing publication info"),
    "no_abbrev": _("Missing abbreviation"),
    "no_repository": _("Missing repository"),
    "repository_refs": _("Total repository references"),
    "no_call_number": _("References missing call number"),
    "types": _("Reference media types"),
}


REPOSITORY_LABELS = {
    "total": _("Number of repositories"),
    "no_name": _("Missing name"),
    "no_address": _("Missing address"),
    "types": _("Repository types"),
}


NOTE_LABELS = {
    "total": _("Number of notes"),
    "no_text": _("Missing text"),
    "types": _("Note types"),
}


TAG_LABELS = {
    "total": _("Number of tags"),
    "male": _("Tagged males"),
    "female": _("Tagged females"),
    "unknown": _("Tagged unknown gender"),
    "family": _("Tagged families"),
    "event": _("Tagged events"),
    "place": _("Tagged places"),
    "media": _("Tagged media"),
    "source": _("Tagged sources"),
    "citation": _("Tagged citations"),
    "repository": _("Tagged repositories"),
    "note": _("Tagged notes"),
}


BOOKMARK_LABELS = {
    "total": _("Number of bookmarks"),
    "person": _("Person bookmarks"),
    "family": _("Family bookmarks"),
    "event": _("Event bookmarks"),
    "place": _("Place bookmarks"),
    "media": _("Media bookmarks"),
    "source": _("Source bookmarks"),
    "citation": _("Citation bookmarks"),
    "repository": _("Repository bookmarks"),
    "note": _("Note bookmarks"),
}
