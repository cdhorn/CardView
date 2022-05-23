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

import os

from gi.repository import Gtk
from gramps.gen.const import USER_PLUGINS

fname = os.path.join(USER_PLUGINS, "CardView", "src", "icons")
icons = Gtk.IconTheme().get_default()
icons.append_search_path(fname)

VERSION = "0.91"
GRAMPS_TARGET_VERSION = "5.1"
AUTHORS = ["The Gramps Project", "Christopher Horn"]
AUTHORS_EMAIL = ["https://gramps-project.org"]

register(
    VIEW,
    id="personcardview",
    name=_("Person"),
    description=_("A browseable Person card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_person.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("People", _("People")),
    viewclass="PersonCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="familycardview",
    name=_("Family"),
    description=_("A browseable Family card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_family.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Families", _("Families")),
    viewclass="FamilyCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="eventcardview",
    name=_("Event"),
    description=_("A browseable Event card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_event.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Events", _("Events")),
    viewclass="EventCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="placecardview",
    name=_("Place"),
    description=_("A browseable Place card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_place.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Places", _("Places")),
    viewclass="PlaceCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="sourcecardview",
    name=_("Source"),
    description=_("A browseable Source card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_source.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Sources", _("Sources")),
    viewclass="SourceCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="citationcardview",
    name=_("Citation"),
    description=_("A browseable Citation card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_citation.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Citations", _("Citations")),
    viewclass="CitationCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="repositorycardview",
    name=_("Repository"),
    description=_("A browseable Repository card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_repository.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Repositories", _("Repositories")),
    viewclass="RepositoryCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="mediacardview",
    name=_("Media"),
    description=_("A browseable Media card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_media.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Media", _("Media")),
    viewclass="MediaCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="notecardview",
    name=_("Note"),
    description=_("A browseable Note card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_note.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Notes", _("Notes")),
    viewclass="NoteCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)

register(
    VIEW,
    id="tagcardview",
    name=_("Tag"),
    description=_("A browseable Tag card view."),
    version=VERSION,
    gramps_target_version=GRAMPS_TARGET_VERSION,
    status=STABLE,
    fname="card_view_tag.py",
    authors=AUTHORS,
    authors_email=AUTHORS_EMAIL,
    category=("Tags", _("Tags")),
    viewclass="TagCardView",
    stock_icon="gramps-relation-linked",
    order=END,
)
