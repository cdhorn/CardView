#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020       Nick Hall
# Copyright (C) 2020       Christian Schulze
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

from gramps.gen.const import USER_PLUGINS
from gramps.gen.config import config

VERSION = "0.99.110"
GRAMPS_TARGET_VERSION = "5.1"
AUTHORS = ["The Gramps Project", "Christopher Horn"]
AUTHORS_EMAIL = ["https://gramps-project.org"]

if not config.has_default("interface.cardview.enable-statistics-dashboard"):
    config.register("interface.cardview.enable-statistics-dashboard", False)
    config.save()
enable_dashboard = config.get("interface.cardview.enable-statistics-dashboard")

if enable_dashboard:
    register(
        VIEW,
        id="statisticscardview",
        name=_("Statistics"),
        description=_("A tree statistics dashboard."),
        version=VERSION,
        gramps_target_version=GRAMPS_TARGET_VERSION,
        status=STABLE,
        fname="card_view_statistics.py",
        authors=AUTHORS,
        authors_email=AUTHORS_EMAIL,
        category=("Dashboard", _("Dashboard")),
        viewclass="StatisticsCardView",
        icondir="%s/CardView/icons" % USER_PLUGINS,
        icons=[("gramps-dashboardcardview", _("Dashboard Card"))],
        stock_icon="gramps-dashboardcardview",
        order=END,
    )

register(
    VIEW,
    id="personcardview",
    name=_("Person Card"),
    description=_("A browseable Person card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_person.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("People", _("People")),
    viewclass="PersonCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-personcard", _("Person Card"))],
    stock_icon="gramps-personcard",
    order=END,
)

register(
    VIEW,
    id="relationshipcardview",
    name=_("Relationships Card"),
    description=_("A browseable Relationships card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_person.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Relationships", _("Relationships")),
    viewclass="PersonCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-relationshipscard", _("Relationships Card"))],
    stock_icon="gramps-relationshipscard",
    order=END,
)

register(
    VIEW,
    id="familycardview",
    name=_("Family Card"),
    description=_("A browseable Family card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_family.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Families", _("Families")),
    viewclass="FamilyCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-familycard", _("Family Card"))],
    stock_icon="gramps-familycard",
    order=END,
)

register(
    VIEW,
    id="eventcardview",
    name=_("Event Card"),
    description=_("A browseable Event card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_event.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Events", _("Events")),
    viewclass="EventCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-eventcard", _("Event Card"))],
    stock_icon="gramps-eventcard",
    order=END,
)

register(
    VIEW,
    id="placecardview",
    name=_("Place Card"),
    description=_("A browseable Place card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_place.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Places", _("Places")),
    viewclass="PlaceCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-placecard", _("Place Card"))],
    stock_icon="gramps-placecard",
    order=END,
)

register(
    VIEW,
    id="sourcecardview",
    name=_("Source Card"),
    description=_("A browseable Source card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_source.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Sources", _("Sources")),
    viewclass="SourceCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-sourcecard", _("Source Card"))],
    stock_icon="gramps-sourcecard",
    order=END,
)

register(
    VIEW,
    id="citationcardview",
    name=_("Citation Card"),
    description=_("A browseable Citation card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_citation.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Citations", _("Citations")),
    viewclass="CitationCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-citationcard", _("Citation Card"))],
    stock_icon="gramps-citationcard",
    order=END,
)

register(
    VIEW,
    id="repositorycardview",
    name=_("Repository Card"),
    description=_("A browseable Repository card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_repository.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Repositories", _("Repositories")),
    viewclass="RepositoryCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-repositorycard", _("Repository Card"))],
    stock_icon="gramps-repositorycard",
    order=END,
)

register(
    VIEW,
    id="mediacardview",
    name=_("Media Card"),
    description=_("A browseable Media card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_media.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Media", _("Media")),
    viewclass="MediaCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-mediacard", _("Media Card"))],
    stock_icon="gramps-mediacard",
    order=END,
)

register(
    VIEW,
    id="notecardview",
    name=_("Note Card"),
    description=_("A browseable Note card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_note.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Notes", _("Notes")),
    viewclass="NoteCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-notecard", _("Note Card"))],
    stock_icon="gramps-notecard",
    order=END,
)

register(
    VIEW,
    id="tagcardview",
    name=_("Tag Card"),
    description=_("A browseable Tag card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_tag.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Tags", _("Tags")),
    viewclass="TagCardView",
    icondir="%s/CardView/icons" % USER_PLUGINS,
    icons=[("gramps-tagcard", _("Tag Card"))],
    stock_icon="gramps-tagcard",
    order=END,
)
