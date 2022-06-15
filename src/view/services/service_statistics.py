#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2010       Jakim Friant
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
StatisticsService
"""

# -------------------------------------------------------------------------
#
# Python Modules
#
# -------------------------------------------------------------------------
import os
from bisect import bisect

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.utils.file import media_path_full
from gramps.gen.datehandler import get_date
from gramps.gen.lib import (
    Citation,
    EventType,
    EventRoleType,
    FamilyRelType,
    Person,
    PlaceType,
    RepositoryType,
)

_ = glocale.translation.sgettext


# -------------------------------------------------------------------------
#
# StatisticsService
#
# -------------------------------------------------------------------------
class StatisticsService:
    """
    A singleton class that collects database statistics.
    """

    __init = False

    def __new__(cls, *args):
        """
        Return the singleton class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(StatisticsService, cls).__new__(cls)
        return cls.instance

    def __init__(self, dbstate):
        """
        Initialize the class if needed.
        """
        if not self.__init:
            self.dbstate = dbstate
            self.facts = []
            self.dbstate.connect("database-changed", self.database_changed)
            self.__init = True

    def database_changed(self, *args):
        """
        Rescan the database.
        """
        if self.dbstate.is_open():
            self.gather_data()
        else:
            self.facts.clear()

    def get_data(self):
        if self.facts == []:
            self.gather_data()
        return self.facts

    def gather_data(self):
        self.facts.clear()

        db = self.dbstate.db
        self.facts = self.facts + analyze_media(db)
        self.facts = self.facts + analyze_people(db)
        self.facts = self.facts + analyze_families(db)
        self.facts = self.facts + analyze_events(db)
        self.facts = self.facts + analyze_places(db)
        self.facts = self.facts + analyze_sources(db)
        self.facts = self.facts + analyze_citations(db)
        self.facts = self.facts + analyze_repositories(db)


def analyze_people(db):
    """
    Parse and analyze people.
    """
    media_total, media_references = 0, 0
    incomp_names, disconnected = 0, 0
    missing_births, uncited_births, private_births = 0, 0, 0
    missing_birth_dates, missing_death_dates = 0, 0
    missing_deaths, uncited_deaths, private_deaths = 0, 0, 0
    males, uncited_males, private_males = 0, 0, 0
    females, uncited_females, private_females = 0, 0, 0
    unknowns, uncited_unknowns, private_unknowns = 0, 0, 0
    refs, refs_total, refs_unknown, refs_private, refs_uncited = 0, 0, 0, 0, 0
    no_role, private_roles = 0, 0
    last_changed = []

    for person in db.iter_people():
        length = len(person.get_media_list())
        if length > 0:
            media_total += 1
            media_references += length

        for name in [person.get_primary_name()] + person.get_alternate_names():
            if name.get_first_name().strip() == "":
                incomp_names += 1
            else:
                if name.get_surname_list():
                    for surname in name.get_surname_list():
                        if surname.get_surname().strip() == "":
                            incomp_names += 1
                else:
                    incomp_names += 1

        if not person.parent_family_list and not person.family_list:
            disconnected += 1

        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = db.get_event_from_handle(birth_ref.ref)
            if not get_date(birth):
                missing_birth_dates += 1
            if not birth.citation_list:
                uncited_births += 1
            if birth.private:
                private_births += 1
        else:
            missing_births += 1

        death_ref = person.get_death_ref()
        if death_ref:
            death = db.get_event_from_handle(death_ref.ref)
            if not get_date(death):
                missing_death_dates += 1
            if not death.citation_list:
                uncited_deaths += 1
            if death.private:
                private_deaths += 1
        else:
            missing_deaths += 1

        if person.get_gender() == Person.FEMALE:
            females += 1
            if not person.citation_list:
                uncited_females += 1
            if person.private:
                private_females += 1
        elif person.get_gender() == Person.MALE:
            males += 1
            if not person.citation_list:
                uncited_males += 1
            if person.private:
                private_males += 1
        else:
            unknowns += 1
            if not person.citation_list:
                uncited_unknowns += 1
            if person.private:
                private_unknowns += 1

        if person.person_ref_list:
            refs += 1
            for ref in person.person_ref_list:
                refs_total += 1
                if ref.private:
                    refs_private += 1
                if not ref.citation_list:
                    refs_uncited += 1
                if not ref.rel:
                    refs_unknown += 1

        for ref in person.event_ref_list:
            if ref.get_role() == EventRoleType.UNKNOWN:
                no_role += 1
            if ref.private:
                private_roles += 1
        analyze_change(last_changed, person.handle, person.change, 20)

    number_people = db.get_number_of_people()
    if not number_people:
        return [(["person"], _("Number of individuals"), 0, None)]

    result = [
        (
            ["changed"],
            _("Most recently modified people"),
            last_changed,
            "Person",
        ),
        (["person"], _("Number of individuals"), number_people, None),
        (["person"], _("Males"), males, males * 100 / number_people),
        (["person"], _("Females"), females, females * 100 / number_people),
        (
            ["person"],
            _("Unknown gender"),
            unknowns,
            unknowns * 100 / number_people,
        ),
        (
            ["person"],
            _("Incomplete names"),
            incomp_names,
            incomp_names * 100 / number_people,
        ),
        (
            ["person"],
            _("Missing birth events"),
            missing_births,
            missing_births * 100 / number_people,
        ),
        (
            ["person"],
            _("Birth events missing dates"),
            missing_birth_dates,
            missing_birth_dates * 100 / number_people,
        ),
        (
            ["person"],
            _("Missing death events"),
            missing_deaths,
            missing_deaths * 100 / number_people,
        ),
        (
            ["person"],
            _("Death events missing dates"),
            missing_death_dates,
            missing_death_dates * 100 / number_people,
        ),
        (
            ["person"],
            _("Unknown event participation roles"),
            no_role,
            None,
        ),
        (
            ["person"],
            _("Disconnected from a family"),
            disconnected,
            disconnected * 100 / number_people,
        ),
        (
            ["media"],
            _("Individuals with media objects"),
            media_total,
            media_total * 100 / number_people,
        ),
        (
            ["media"],
            _("Total individual media object references"),
            media_references,
            None,
        ),
        (
            ["person"],
            _("People with associations"),
            refs,
            refs * 100 / number_people,
        ),
    ]

    if refs_total:
        result = result + [
            (
                ["person"],
                _("Total association references"),
                refs_total,
                None,
            ),
            (
                ["person"],
                _("Unknown association type"),
                refs_unknown,
                refs_unknown * 100 / refs_total,
            ),
        ]

    if males:
        result = result + [
            (
                ["quality"],
                _("Males with no supporting citations"),
                uncited_males,
                uncited_males * 100 / males,
            ),
            (
                ["privacy"],
                _("Private males"),
                private_males,
                private_males * 100 / males,
            ),
        ]

    if females:
        result = result + [
            (
                ["quality"],
                _("Females with no supporting citation"),
                uncited_females,
                uncited_females * 100 / females,
            ),
            (
                ["privacy"],
                _("Private females"),
                private_females,
                private_females * 100 / females,
            ),
        ]

    if unknowns:
        result = result + [
            (
                ["quality"],
                _("Unknown genders with no supporting citation"),
                uncited_unknowns,
                uncited_unknowns * 100 / unknowns,
            ),
            (
                ["privacy"],
                _("Private unknown genders"),
                private_unknowns,
                private_unknowns * 100 / unknowns,
            ),
        ]

    number_people_with_births = number_people - missing_births
    if number_people_with_births:
        result = result + [
            (
                ["quality"],
                _("Preferred births with no supporting citation"),
                uncited_births,
                uncited_births * 100 / number_people_with_births,
            ),
            (
                ["privacy"],
                _("Private preferred births"),
                private_births,
                private_births * 100 / number_people_with_births,
            ),
        ]

    number_people_with_deaths = number_people - missing_deaths
    if number_people_with_deaths:
        result = result + [
            (
                ["quality"],
                _("Preferred deaths with no supporting citation"),
                uncited_deaths,
                uncited_deaths * 100 / number_people_with_deaths,
            ),
            (
                ["privacy"],
                _("Private preferred deaths"),
                private_deaths,
                private_deaths * 100 / number_people_with_deaths,
            ),
        ]

    result = result + [
        (
            ["privacy"],
            _("Private individual event participants"),
            private_roles,
            None,
        ),
    ]
    if refs_total:
        result = result + [
            (
                ["quality"],
                _("Associations with no supporting citation"),
                refs_uncited,
                refs_uncited * 100 / refs_total,
            ),
            (
                ["privacy"],
                _("Private associations"),
                refs_private,
                refs_private * 100 / refs_total,
            ),
        ]
    return result


def analyze_families(db):
    """
    Parse and analyze families.
    """
    media_total, media_references = 0, 0
    missing_one_partner, missing_both_partners, unknown_relation = 0, 0, 0
    no_citations, no_events, no_children, private = 0, 0, 0, 0
    refs, refs_private, refs_uncited = 0, 0, 0
    no_role, private_roles = 0, 0
    last_changed = []

    for family in db.iter_families():
        length = len(family.media_list)
        if length > 0:
            media_total += 1
            media_references += length
        if family.type == FamilyRelType.UNKNOWN:
            unknown_relation += 1
        if not family.citation_list:
            no_citations += 1
        if not family.event_ref_list:
            no_events += 1
        else:
            for ref in family.event_ref_list:
                if ref.get_role() == EventRoleType.UNKNOWN:
                    no_role += 1
                if ref.private:
                    private_roles += 1
        if not family.child_ref_list:
            no_children += 1
        else:
            for ref in family.child_ref_list:
                refs += 1
                if ref.private:
                    refs_private += 1
                if not ref.citation_list:
                    refs_uncited += 1
        if family.private:
            private += 1
        if not family.father_handle and not family.mother_handle:
            missing_both_partners += 1
        elif not family.father_handle or not family.mother_handle:
            missing_one_partner += 1
        analyze_change(last_changed, family.handle, family.change, 20)

    number_families = db.get_number_of_families()
    if not number_families:
        return [(["family"], _("Number of families"), 0, None)]

    result = [
        (
            ["changed"],
            _("Most recently modified families"),
            last_changed,
            "Family",
        ),
        (["family"], _("Number of families"), number_families, None),
        (["family"], _("Unique surnames"), len(set(db.surname_list)), None),
        (
            ["family"],
            _("Unknown relationship type"),
            unknown_relation,
            unknown_relation * 100 / number_families,
        ),
        (
            ["family"],
            _("Only one spouse found"),
            missing_one_partner,
            missing_one_partner * 100 / number_families,
        ),
        (
            ["family"],
            _("No spouses found"),
            missing_both_partners,
            missing_both_partners * 100 / number_families,
        ),
        (
            ["family"],
            _("No events found"),
            no_events,
            no_events * 100 / number_families,
        ),
        (
            ["family"],
            _("Unknown event participation roles"),
            no_role,
            None,
        ),
        (
            ["family"],
            _("No children found"),
            no_children,
            no_children * 100 / number_families,
        ),
        (
            ["quality"],
            _("Families with no supporting citation"),
            no_citations,
            no_citations * 100 / number_families,
        ),
        (
            ["privacy"],
            _("Private families"),
            private,
            private * 100 / number_families,
        ),
        (
            ["privacy"],
            _("Private family event participant roles"),
            private_roles,
            None,
        ),
    ]

    if refs:
        result = result + [
            (
                ["quality"],
                _("Children with no supporting citation"),
                refs_uncited,
                refs_uncited * 100 / refs,
            ),
            (
                ["privacy"],
                _("Private children"),
                refs_private,
                refs_private * 100 / refs,
            ),
        ]

    result = result + [
        (
            ["media"],
            _("Families with media objects"),
            media_total,
            media_total * 100 / number_families,
        ),
        (
            ["media"],
            _("Total number of family media object references"),
            media_references,
            None,
        ),
    ]
    return result


def analyze_events(db):
    """
    Parse and analyze events.
    """
    media_total, media_references = 0, 0
    no_date, no_place, no_description, no_type = 0, 0, 0, 0
    no_citations, private = 0, 0
    last_changed = []

    for event in db.iter_events():
        length = len(event.media_list)
        if length > 0:
            media_total += 1
            media_references += length
        if not event.citation_list:
            no_citations += 1
        if not event.place:
            no_place += 1
        if not get_date(event):
            no_date += 1
        if not event.get_description():
            no_description += 1
        if event.get_type() == EventType.UNKNOWN:
            no_type += 1
        if event.private:
            private += 1
        analyze_change(last_changed, event.handle, event.change, 20)

    number_events = db.get_number_of_events()
    if not number_events:
        return [(["event"], _("Number of events"), 0, None)]

    return [
        (
            ["changed"],
            _("Most recently modified events"),
            last_changed,
            "Event",
        ),
        (["event"], _("Number of events"), number_events, None),
        (
            ["event"],
            _("Missing date"),
            no_date,
            no_date * 100 / number_events,
        ),
        (
            ["event"],
            _("Missing place"),
            no_place,
            no_place * 100 / number_events,
        ),
        (
            ["event"],
            _("Missing description"),
            no_description,
            no_description * 100 / number_events,
        ),
        (
            ["event"],
            _("Unknown event type"),
            no_type,
            no_type * 100 / number_events,
        ),
        (
            ["quality"],
            _("Events with no supporting citation"),
            no_citations,
            no_citations * 100 / number_events,
        ),
        (
            ["privacy"],
            _("Private events"),
            private,
            private * 100 / number_events,
        ),
        (
            ["media"],
            _("Events with media objects"),
            media_total,
            media_total * 100 / number_events,
        ),
        (
            ["media"],
            _("Total number of event media object references"),
            media_references,
            None,
        ),
    ]


def analyze_places(db):
    """
    Parse and analyze places.
    """
    media_total, media_references = 0, 0
    no_name, no_type, no_latitude, no_longitude, no_code = 0, 0, 0, 0, 0
    no_citations, private = 0, 0
    last_changed = []

    for place in db.iter_places():
        length = len(place.media_list)
        if length > 0:
            media_total += 1
            media_references += length
        if not place.name:
            no_name += 1
        if place.get_type() == PlaceType.UNKNOWN:
            no_type += 1
        if not place.lat:
            no_latitude += 1
        if not place.long:
            no_longitude += 1
        if not place.code:
            no_code += 1
        if not place.citation_list:
            no_citations += 1
        if place.private:
            private += 1
        analyze_change(last_changed, place.handle, place.change, 20)

    number_places = db.get_number_of_places()
    if not number_places:
        return [(["place"], _("Number of places"), 0, None)]

    return [
        (
            ["changed"],
            _("Most recently modified places"),
            last_changed,
            "Place",
        ),
        (["place"], _("Number of places"), number_places, None),
        (
            ["place"],
            _("Missing name"),
            no_name,
            no_name * 100 / number_places,
        ),
        (
            ["place"],
            _("Missing latitude"),
            no_latitude,
            no_latitude * 100 / number_places,
        ),
        (
            ["place"],
            _("Missing longitude"),
            no_longitude,
            no_longitude * 100 / number_places,
        ),
        (
            ["place"],
            _("Missing place code"),
            no_code,
            no_code * 100 / number_places,
        ),
        (
            ["place"],
            _("Unknown place type"),
            no_type,
            no_type * 100 / number_places,
        ),
        (
            ["quality"],
            _("Places with no supporting citations"),
            no_citations,
            no_citations * 100 / number_places,
        ),
        (
            ["privacy"],
            _("Private places"),
            private,
            private * 100 / number_places,
        ),
        (
            ["media"],
            _("Places with media objects"),
            media_total,
            media_total * 100 / number_places,
        ),
        (
            ["media"],
            _("Total number of place media object references"),
            media_references,
            None,
        ),
    ]


def analyze_media(db):
    """
    Parse and analyze media objects.
    """
    bytes_cnt, private, no_desc = 0, 0, 0
    notfound = []
    last_changed = []

    mbytes = "0"
    for media in db.iter_media():
        if media.private:
            private += 1
        if not media.desc:
            no_desc += 1
        fullname = media_path_full(db, media.get_path())
        try:
            bytes_cnt += os.path.getsize(fullname)
            length = len(str(bytes_cnt))
            if bytes_cnt <= 999999:
                mbytes = _("less than 1")
            else:
                mbytes = str(bytes_cnt)[: (length - 6)]
        except OSError:
            notfound.append(media.get_path())
        analyze_change(last_changed, media.handle, media.change, 20)

    number_media = db.get_number_of_media()
    if not number_media:
        return [(["media"], _("Number of unique media items"), 0, None)]

    return [
        (
            ["changed"],
            _("Most recently modified media objects"),
            last_changed,
            "Media",
        ),
        (["media"], _("Number of unique media items"), number_media, None),
        (
            ["media"],
            _("Total size of media objects"),
            " %s %s" % (mbytes, _("MB", "Megabyte")),
            None,
        ),
        (
            ["media"],
            _("Missing media objects"),
            str(len(notfound)),
            len(notfound) * 100 / number_media,
        ),
        (
            ["media"],
            _("Media objects with no description"),
            no_desc,
            no_desc * 100 / number_media,
        ),
        (
            ["privacy"],
            _("Private media objects"),
            private,
            private * 100 / number_media,
        ),
    ]


def analyze_sources(db):
    """
    Parse and analyze sources.
    """
    media_total, media_references = 0, 0
    no_title, no_author, no_pubinfo, no_abbrev = 0, 0, 0, 0
    no_repository, private = 0, 0
    last_changed = []

    for source in db.iter_sources():
        length = len(source.media_list)
        if length > 0:
            media_total += 1
            media_references += length
        if not source.reporef_list:
            no_repository += 1
        if not source.title:
            no_title += 1
        if not source.author:
            no_author += 1
        if not source.pubinfo:
            no_pubinfo += 1
        if not source.abbrev:
            no_abbrev += 1
        if source.private:
            private += 1
        analyze_change(last_changed, source.handle, source.change, 20)

    number_sources = db.get_number_of_sources()
    if not number_sources:
        return [(["source"], _("Number of sources"), 0, None)]

    return [
        (
            ["changed"],
            _("Most recently modified sources"),
            last_changed,
            "Source",
        ),
        (["source"], _("Number of sources"), number_sources, None),
        (
            ["source"],
            _("Missing title"),
            no_title,
            no_title * 100 / number_sources,
        ),
        (
            ["source"],
            _("Missing author"),
            no_author,
            no_author * 100 / number_sources,
        ),
        (
            ["source"],
            _("Missing publication info"),
            no_pubinfo,
            no_pubinfo * 100 / number_sources,
        ),
        (
            ["source"],
            _("Missing abbreviation"),
            no_abbrev,
            no_abbrev * 100 / number_sources,
        ),
        (
            ["source"],
            _("Missing repository"),
            no_repository,
            no_repository * 100 / number_sources,
        ),
        (
            ["privacy"],
            _("Private sources"),
            private,
            private * 100 / number_sources,
        ),
        (
            ["media"],
            _("Sources with media objects"),
            media_total,
            media_total * 100 / number_sources,
        ),
        (
            ["media"],
            _("Total number of source media object references"),
            media_references,
            None,
        ),
    ]


def analyze_citations(db):
    """
    Parse and analyze citation objects.
    """
    media_total, media_references = 0, 0
    missing_source, missing_page, no_date, private = 0, 0, 0, 0
    very_low, low, normal, high, very_high = 0, 0, 0, 0, 0
    last_changed = []

    for citation in db.iter_citations():
        length = len(citation.media_list)
        if length > 0:
            media_total += 1
            media_references += length
        if citation.private:
            private += 1
        if not get_date(citation):
            no_date += 1
        if not citation.source_handle:
            missing_source += 1
        if not citation.page:
            missing_page += 1
        if citation.confidence == Citation.CONF_VERY_LOW:
            very_low += 1
        elif citation.confidence == Citation.CONF_LOW:
            low += 1
        elif citation.confidence == Citation.CONF_NORMAL:
            normal += 1
        elif citation.confidence == Citation.CONF_HIGH:
            high += 1
        elif citation.confidence == Citation.CONF_VERY_HIGH:
            very_high += 1
        analyze_change(last_changed, citation.handle, citation.change, 20)

    number_citations = db.get_number_of_citations()
    if not number_citations:
        return [(["citations"], _("Number of citations"), 0, None)]

    return [
        (
            ["changed"],
            _("Most recently modified citation objects"),
            last_changed,
            "Citation",
        ),
        (["citation"], _("Number of citations"), number_citations, None),
        (
            ["citation"],
            _("Missing source"),
            missing_source,
            missing_source * 100 / number_citations,
        ),
        (
            ["citation"],
            _("Missing page"),
            missing_page,
            missing_page * 100 / number_citations,
        ),
        (
            ["citation"],
            _("Missing date"),
            no_date,
            no_date * 100 / number_citations,
        ),
        (
            ["citation"],
            _("Very low confidence"),
            very_low,
            very_low * 100 / number_citations,
        ),
        (["citation"], _("Low confidence"), low, low * 100 / number_citations),
        (
            ["citation"],
            _("Normal confidence"),
            normal,
            normal * 100 / number_citations,
        ),
        (
            ["citation"],
            _("High confidence"),
            high,
            high * 100 / number_citations,
        ),
        (
            ["citation"],
            _("Very high confidence"),
            very_high,
            very_high * 100 / number_citations,
        ),
        (
            ["privacy"],
            _("Private citations"),
            private,
            private * 100 / number_citations,
        ),
        (
            ["media"],
            _("Citations with media objects"),
            media_total,
            media_total * 100 / number_citations,
        ),
        (
            ["media"],
            _("Total number of citation media object references"),
            media_references,
            None,
        ),
    ]


def analyze_repositories(db):
    """
    Parse and analyze repositories.
    """
    no_name, no_address, no_type, private = 0, 0, 0, 0
    last_changed = []

    for repository in db.iter_repositories():
        if not repository.name:
            no_name += 1
        if not repository.address_list:
            no_address += 1
        if repository.get_type() == RepositoryType.UNKNOWN:
            no_type += 1
        if repository.private:
            private += 1
        analyze_change(last_changed, repository.handle, repository.change, 20)

    number_repositories = db.get_number_of_repositories()
    if not number_repositories:
        return [(["repository"], _("Number of repositories"), 0, None)]

    return [
        (
            ["changed"],
            _("Most recently modified repositories"),
            last_changed,
            "Repository",
        ),
        (
            ["repository"],
            _("Number of repositories"),
            number_repositories,
            None,
        ),
        (
            ["repository"],
            _("Missing name"),
            no_name,
            no_name * 100 / number_repositories,
        ),
        (
            ["repository"],
            _("Missing address"),
            no_address,
            no_address * 100 / number_repositories,
        ),
        (
            ["repository"],
            _("Unknown repository type"),
            no_type,
            no_type * 100 / number_repositories,
        ),
        (
            ["privacy"],
            _("Private repositories"),
            private,
            private * 100 / number_repositories,
        ),
    ]


def analyze_change(obj_list, obj_handle, change, max_length):
    """
    Analyze a change for inclusion in a last modified list.
    """
    bsindex = bisect(KeyWrapper(obj_list, key=lambda c: c[1]), change)
    obj_list.insert(bsindex, (obj_handle, change))
    if len(obj_list) > max_length:
        obj_list.pop(max_length)


# ------------------------------------------------------------------------
#
# KeyWrapper class
#
# ------------------------------------------------------------------------
class KeyWrapper:
    """
    For bisect to operate on an element of a tuple in the list.
    """

    __slots__ = "iter", "key"

    def __init__(self, iterable, key):
        self.iter = iterable
        self.key = key

    def __getitem__(self, i):
        return self.key(self.iter[i])

    def __len__(self):
        return len(self.iter)
