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
Minimal baseline card view template plugin.
"""

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext


_TEMPLATE = (
    ######################################################################
    ## Template Management Options
    ######################################################################
    ("template.type", "cardview"),
    ("template.xml_string", "Minimal"),
    ("template.lang_string", _("Minimal")),
    ("template.description", _("Minimal view template")),
    ("template.comments", []),
    ("template.normal_baseline", ""),
    ("template.active_baseline", ""),
    ######################################################################
    # Global Options
    #
    ######################################################################
    ## Display Options
    ######################################################################
    ("display.max-page-windows", 1),
    ("display.max-group-windows", 1),
    ("display.pin-header", False),
    ("display.focal-object-highlight", False),
    ("display.focal-object-color", ["#bbe68a", "#304918"]),
    (
        "display.default-background-color",
        ["#eeeeee", "#454545"],
    ),
    ("display.default-foreground-color", ["#454545", "#eeeeee"]),
    ("display.use-color-scheme", True),
    ("display.use-smaller-title-font", True),
    ("display.use-smaller-detail-font", True),
    ("display.use-smaller-icons", True),
    ("display.group-mode", 0),
    ("display.border-width", 2),
    ("display.icons-active-width", 24),
    ("display.icons-group-width", 12),
    ######################################################################
    ## General Options
    ######################################################################
    ("general.concurrent-threshold", 50000),
    ("general.summarize-all-events", False),
    ("general.link-people-to-relationships-view", False),
    ("general.image-page-link", True),
    ("general.link-citation-title-to-source", True),
    ("general.create-reciprocal-associations", True),
    ("general.include-child-notes", True),
    ("general.include-note-urls", True),
    ("general.enable-warnings", True),
    ("general.zotero-enabled", True),
    ("general.zotero-enabled-notes", False),
    ("general.references-max-per-group", 200),
    ######################################################################
    ## Menu Options
    ######################################################################
    ("menu.delete", True),
    ("menu.delete-bottom", False),
    ("menu.delete-submenus", True),
    ("menu.set-home-person", True),
    ("menu.go-to-person", True),
    ("menu.parents", True),
    ("menu.spouses", True),
    ("menu.associations", True),
    ("menu.participants", True),
    ("menu.names", True),
    ("menu.attributes", True),
    ("menu.ordinances", True),
    ("menu.enclosed-places", True),
    ("menu.citations", True),
    ("menu.repositories", True),
    ("menu.media", True),
    ("menu.notes", True),
    ("menu.notes-children", True),
    ("menu.urls", True),
    ("menu.tags", True),
    ("menu.clipboard", True),
    ("menu.bookmarks", True),
    ("menu.privacy", True),
    ######################################################################
    # Basic Indicator Related Options
    ######################################################################
    ("indicator.gramps-ids", False),
    ("indicator.privacy", 0),
    ("indicator.bookmarks", False),
    ("indicator.home-person", False),
    ("indicator.tags", False),
    ("indicator.tags-sort-by-name", False),
    ("indicator.tags-max-displayed", 1),
    ("indicator.child-objects", False),
    ("indicator.child-objects-counts", False),
    ("indicator.names", True),
    ("indicator.parents", True),
    ("indicator.spouses", True),
    ("indicator.children", True),
    ("indicator.associations", True),
    ("indicator.events", True),
    ("indicator.ordinances", True),
    ("indicator.media", True),
    ("indicator.attributes", True),
    ("indicator.addresses", True),
    ("indicator.citations", True),
    ("indicator.notes", True),
    ("indicator.urls", True),
    ######################################################################
    ## Media Bar Related Options
    ######################################################################
    ("media-bar.enabled", False),
    ("media-bar.position", 1),
    ("media-bar.display-mode", 1),
    ("media-bar.minimum-required", 1),
    ("media-bar.sort-by-date", True),
    ("media-bar.group-by-type", True),
    ("media-bar.filter-non-photos", False),
    ("media-bar.page-link", True),
    ######################################################################
    # Card Level Options
    # These apply when the card is in the page header and not a group
    #
    ######################################################################
    ## Person Options
    ######################################################################
    ("active.person.event-format", 1),
    ("active.person.show-age", True),
    ("active.person.sex-mode", 1),
    ("active.person.image-mode", 3),
    ("active.person.show-parents", False),
    ("active.person.compact-mode-parents", False),
    ("active.person.lfield-skip-birth-alternates", True),
    ("active.person.lfield-skip-death-alternates", True),
    ("active.person.lfield-1", "Event:Birth"),
    ("active.person.lfield-2", "Event:Baptism"),
    ("active.person.lfield-3", "Event:Christening"),
    ("active.person.lfield-4", "Event:Death"),
    ("active.person.lfield-5", "Event:Cremation"),
    ("active.person.lfield-6", "Event:Burial"),
    ("active.person.lfield-7", "None"),
    ("active.person.lfield-8", "None"),
    ("active.person.lfield-9", "None"),
    ("active.person.lfield-10", "None"),
    ("active.person.mfield-skip-birth-alternates", True),
    ("active.person.mfield-skip-death-alternates", True),
    ("active.person.mfield-1", "None"),
    ("active.person.mfield-2", "None"),
    ("active.person.mfield-3", "None"),
    ("active.person.mfield-4", "None"),
    ("active.person.mfield-5", "None"),
    ("active.person.mfield-6", "None"),
    ("active.person.mfield-7", "None"),
    ("active.person.mfield-8", "None"),
    ("active.person.mfield-9", "None"),
    ("active.person.mfield-10", "None"),
    ("active.person.rfield-show-labels", False),
    ("active.person.rfield-1", "None"),
    ("active.person.rfield-2", "None"),
    ("active.person.rfield-3", "None"),
    ("active.person.rfield-4", "None"),
    ("active.person.rfield-5", "None"),
    ("active.person.rfield-6", "None"),
    ("active.person.rfield-7", "None"),
    ("active.person.rfield-8", "None"),
    ("active.person.rfield-9", "None"),
    ("active.person.rfield-10", "None"),
    ######################################################################
    ## Parent Options
    ######################################################################
    ("active.parent.event-format", 1),
    ("active.parent.show-age", True),
    ("active.parent.sex-mode", 1),
    ("active.parent.image-mode", 3),
    ("active.parent.lfield-skip-birth-alternates", True),
    ("active.parent.lfield-skip-death-alternates", True),
    ("active.parent.lfield-1", "Event:Birth"),
    ("active.parent.lfield-2", "Event:Baptism"),
    ("active.parent.lfield-3", "Event:Christening"),
    ("active.parent.lfield-4", "Event:Death"),
    ("active.parent.lfield-5", "Event:Cremation"),
    ("active.parent.lfield-6", "Event:Burial"),
    ("active.parent.lfield-7", "None"),
    ("active.parent.lfield-8", "None"),
    ("active.parent.lfield-9", "None"),
    ("active.parent.lfield-10", "None"),
    ("active.parent.rfield-show-labels", False),
    ("active.parent.rfield-1", "None"),
    ("active.parent.rfield-2", "None"),
    ("active.parent.rfield-3", "None"),
    ("active.parent.rfield-4", "None"),
    ("active.parent.rfield-5", "None"),
    ("active.parent.rfield-6", "None"),
    ("active.parent.rfield-7", "None"),
    ("active.parent.rfield-8", "None"),
    ("active.parent.rfield-9", "None"),
    ("active.parent.rfield-10", "None"),
    ######################################################################
    ## Spouse Options
    ######################################################################
    ("active.spouse.event-format", 1),
    ("active.spouse.show-age", True),
    ("active.spouse.sex-mode", 1),
    ("active.spouse.image-mode", 3),
    ("active.spouse.lfield-skip-birth-alternates", True),
    ("active.spouse.lfield-skip-death-alternates", True),
    ("active.spouse.lfield-1", "Event:Birth"),
    ("active.spouse.lfield-2", "Event:Baptism"),
    ("active.spouse.lfield-3", "Event:Christening"),
    ("active.spouse.lfield-4", "Event:Death"),
    ("active.spouse.lfield-5", "Event:Christening"),
    ("active.spouse.lfield-6", "Event:Burial"),
    ("active.spouse.lfield-7", "None"),
    ("active.spouse.lfield-8", "None"),
    ("active.spouse.lfield-9", "None"),
    ("active.spouse.lfield-10", "None"),
    ("active.spouse.rfield-show-labels", False),
    ("active.spouse.rfield-1", "None"),
    ("active.spouse.rfield-2", "None"),
    ("active.spouse.rfield-3", "None"),
    ("active.spouse.rfield-4", "None"),
    ("active.spouse.rfield-5", "None"),
    ("active.spouse.rfield-6", "None"),
    ("active.spouse.rfield-7", "None"),
    ("active.spouse.rfield-8", "None"),
    ("active.spouse.rfield-9", "None"),
    ("active.spouse.rfield-10", "None"),
    ######################################################################
    ## Association Options
    ######################################################################
    ("active.association.event-format", 1),
    ("active.association.show-age", True),
    ("active.association.sex-mode", 1),
    ("active.association.image-mode", 3),
    ("active.association.lfield-skip-birth-alternates", True),
    ("active.association.lfield-skip-death-alternates", True),
    ("active.association.lfield-1", "Event:Birth"),
    ("active.association.lfield-2", "Event:Baptism"),
    ("active.association.lfield-3", "Event:Christening"),
    ("active.association.lfield-4", "Event:Death"),
    ("active.association.lfield-5", "Event:Cremation"),
    ("active.association.lfield-6", "Event:Burial"),
    ("active.association.lfield-7", "None"),
    ("active.association.lfield-8", "None"),
    ("active.association.lfield-9", "None"),
    ("active.association.lfield-10", "None"),
    ("active.association.rfield-show-labels", False),
    ("active.association.rfield-1", "None"),
    ("active.association.rfield-2", "None"),
    ("active.association.rfield-3", "None"),
    ("active.association.rfield-4", "None"),
    ("active.association.rfield-5", "None"),
    ("active.association.rfield-6", "None"),
    ("active.association.rfield-7", "None"),
    ("active.association.rfield-8", "None"),
    ("active.association.rfield-9", "None"),
    ("active.association.rfield-10", "None"),
    ######################################################################
    ## Family Options
    ######################################################################
    ("active.family.event-format", 1),
    ("active.family.image-mode", 3),
    ("active.family.compact-mode", False),
    ("active.family.show-parents", True),
    ("active.family.compact-mode-parents", True),
    ("active.family.lfield-skip-marriage-alternates", True),
    ("active.family.lfield-skip-divorce-alternates", True),
    ("active.family.lfield-1", "Event:Marriage Banns"),
    ("active.family.lfield-2", "Event:Marriage"),
    ("active.family.lfield-3", "Event:Divorce"),
    ("active.family.lfield-4", "None"),
    ("active.family.lfield-5", "None"),
    ("active.family.lfield-6", "None"),
    ("active.family.lfield-7", "None"),
    ("active.family.lfield-8", "None"),
    ("active.family.lfield-9", "None"),
    ("active.family.lfield-10", "None"),
    ("active.family.mfield-skip-marriage-alternates", True),
    ("active.family.mfield-skip-divorce-alternates", True),
    ("active.family.mfield-1", "None"),
    ("active.family.mfield-2", "None"),
    ("active.family.mfield-3", "None"),
    ("active.family.mfield-4", "None"),
    ("active.family.mfield-5", "None"),
    ("active.family.mfield-6", "None"),
    ("active.family.mfield-7", "None"),
    ("active.family.mfield-8", "None"),
    ("active.family.mfield-9", "None"),
    ("active.family.mfield-10", "None"),
    ("active.family.rfield-show-labels", False),
    ("active.family.rfield-1", "None"),
    ("active.family.rfield-2", "None"),
    ("active.family.rfield-3", "None"),
    ("active.family.rfield-4", "None"),
    ("active.family.rfield-5", "None"),
    ("active.family.rfield-6", "None"),
    ("active.family.rfield-7", "None"),
    ("active.family.rfield-8", "None"),
    ("active.family.rfield-9", "None"),
    ("active.family.rfield-10", "None"),
    ######################################################################
    ## Event Options
    ######################################################################
    ("active.event.event-format", 1),
    ("active.event.image-mode", 3),
    ("active.event.color-scheme", 1),
    ("active.event.rfield-show-labels", False),
    ("active.event.rfield-1", "None"),
    ("active.event.rfield-2", "None"),
    ("active.event.rfield-3", "None"),
    ("active.event.rfield-4", "None"),
    ("active.event.rfield-5", "None"),
    ("active.event.show-description", False),
    ("active.event.show-participants", False),
    ("active.event.show-role-always", False),
    ("active.event.show-source-count", False),
    ("active.event.show-citation-count", False),
    ("active.event.show-best-confidence", False),
    ######################################################################
    ## Place Options
    ######################################################################
    ("active.place.image-mode", 3),
    ######################################################################
    ## Citation Options
    ######################################################################
    ("active.citation.image-mode", 3),
    ("active.citation.sort-by-date", False),
    ("active.citation.include-indirect", True),
    ("active.citation.include-parent-family", True),
    ("active.citation.include-family", True),
    ("active.citation.include-family-indirect", True),
    ("active.citation.show-age", True),
    ("active.citation.show-date", True),
    ("active.citation.show-publisher", True),
    ("active.citation.show-reference-type", True),
    ("active.citation.show-reference-description", True),
    ("active.citation.show-confidence", True),
    ("active.citation.rfield-show-labels", False),
    ("active.citation.rfield-1", "None"),
    ("active.citation.rfield-2", "None"),
    ("active.citation.rfield-3", "None"),
    ("active.citation.rfield-4", "None"),
    ("active.citation.rfield-5", "None"),
    ######################################################################
    ## Source Options
    ######################################################################
    ("active.source.event-format", 1),
    ("active.source.image-mode", 3),
    ("active.source.rfield-show-labels", False),
    ("active.source.rfield-1", "None"),
    ("active.source.rfield-2", "None"),
    ("active.source.rfield-3", "None"),
    ("active.source.rfield-4", "None"),
    ("active.source.rfield-5", "None"),
    ######################################################################
    ## Repository Options
    ######################################################################
    ("active.repository.show-call-number", True),
    ("active.repository.show-media-type", True),
    ("active.repository.show-repository-type", True),
    ######################################################################
    ## Media Options
    ######################################################################
    ("active.media.image-mode", 3),
    ("active.media.show-date", True),
    ("active.media.show-path", True),
    ("active.media.show-mime-type", True),
    ("active.media.rfield-show-labels", False),
    ("active.media.rfield-1", "None"),
    ("active.media.rfield-2", "None"),
    ("active.media.rfield-3", "None"),
    ("active.media.rfield-4", "None"),
    ("active.media.rfield-5", "None"),
    ######################################################################
    ## Note Options
    ######################################################################
    ("active.note.text-on-top", False),
    ("active.note.preview-mode", False),
    ("active.note.preview-lines", 3),
    ######################################################################
    # Group Level Options
    # These apply when the card is in a group and not the page header
    #
    ######################################################################
    ## Person Options
    ######################################################################
    ("group.person.event-format", 1),
    ("group.person.show-age", True),
    ("group.person.sex-mode", 1),
    ("group.person.image-mode", 0),
    ("group.person.lfield-skip-birth-alternates", True),
    ("group.person.lfield-skip-death-alternates", True),
    ("group.person.lfield-1", "Event:Birth"),
    ("group.person.lfield-2", "Event:Baptism"),
    ("group.person.lfield-3", "Event:Christening"),
    ("group.person.lfield-4", "Event:Death"),
    ("group.person.lfield-5", "Event:Cremation"),
    ("group.person.lfield-6", "Event:Burial"),
    ("group.person.lfield-7", "None"),
    ("group.person.lfield-8", "None"),
    ("group.person.lfield-9", "None"),
    ("group.person.lfield-10", "None"),
    ("group.person.mfield-skip-birth-alternates", True),
    ("group.person.mfield-skip-death-alternates", True),
    ("group.person.mfield-1", "None"),
    ("group.person.mfield-2", "None"),
    ("group.person.mfield-3", "None"),
    ("group.person.mfield-4", "None"),
    ("group.person.mfield-5", "None"),
    ("group.person.mfield-6", "None"),
    ("group.person.mfield-7", "None"),
    ("group.person.mfield-8", "None"),
    ("group.person.mfield-9", "None"),
    ("group.person.mfield-10", "None"),
    ("group.person.rfield-show-labels", False),
    ("group.person.rfield-1", "None"),
    ("group.person.rfield-2", "None"),
    ("group.person.rfield-3", "None"),
    ("group.person.rfield-4", "None"),
    ("group.person.rfield-5", "None"),
    ("group.person.rfield-6", "None"),
    ("group.person.rfield-7", "None"),
    ("group.person.rfield-8", "None"),
    ("group.person.rfield-9", "None"),
    ("group.person.rfield-10", "None"),
    ######################################################################
    ## Paternal Options
    ######################################################################
    ("group.paternal.display-mode", 0),
    ######################################################################
    ## Maternal Options
    ######################################################################
    ("group.maternal.display-mode", 0),
    ######################################################################
    ## Parent Options
    ######################################################################
    ("group.parent.event-format", 1),
    ("group.parent.show-age", True),
    ("group.parent.sex-mode", 1),
    ("group.parent.image-mode", 0),
    ("group.parent.lfield-skip-birth-alternates", True),
    ("group.parent.lfield-skip-death-alternates", True),
    ("group.parent.lfield-1", "Event:Birth"),
    ("group.parent.lfield-2", "Event:Baptism"),
    ("group.parent.lfield-3", "Event:Christening"),
    ("group.parent.lfield-4", "Event:Death"),
    ("group.parent.lfield-5", "Event:Cremation"),
    ("group.parent.lfield-6", "Event:Burial"),
    ("group.parent.lfield-7", "None"),
    ("group.parent.lfield-8", "None"),
    ("group.parent.lfield-9", "None"),
    ("group.parent.lfield-10", "None"),
    ("group.parent.rfield-show-labels", False),
    ("group.parent.rfield-1", "None"),
    ("group.parent.rfield-2", "None"),
    ("group.parent.rfield-3", "None"),
    ("group.parent.rfield-4", "None"),
    ("group.parent.rfield-5", "None"),
    ("group.parent.rfield-6", "None"),
    ("group.parent.rfield-7", "None"),
    ("group.parent.rfield-8", "None"),
    ("group.parent.rfield-9", "None"),
    ("group.parent.rfield-10", "None"),
    ######################################################################
    ## Sibling Options
    ######################################################################
    ("group.sibling.event-format", 1),
    ("group.sibling.show-age", True),
    ("group.sibling.sex-mode", 1),
    ("group.sibling.image-mode", 0),
    ("group.sibling.number-children", True),
    ("group.sibling.reference-mode", 0),
    ("group.sibling.lfield-skip-birth-alternates", True),
    ("group.sibling.lfield-skip-death-alternates", True),
    ("group.sibling.lfield-1", "Event:Birth"),
    ("group.sibling.lfield-2", "Event:Baptism"),
    ("group.sibling.lfield-3", "Event:Christening"),
    ("group.sibling.lfield-4", "Event:Death"),
    ("group.sibling.lfield-5", "Event:Cremation"),
    ("group.sibling.lfield-6", "Event:Burial"),
    ("group.sibling.lfield-7", "None"),
    ("group.sibling.lfield-8", "None"),
    ("group.sibling.lfield-9", "None"),
    ("group.sibling.lfield-10", "None"),
    ("group.sibling.rfield-show-labels", False),
    ("group.sibling.rfield-1", "None"),
    ("group.sibling.rfield-2", "None"),
    ("group.sibling.rfield-3", "None"),
    ("group.sibling.rfield-4", "None"),
    ("group.sibling.rfield-5", "None"),
    ("group.sibling.rfield-6", "None"),
    ("group.sibling.rfield-7", "None"),
    ("group.sibling.rfield-8", "None"),
    ("group.sibling.rfield-9", "None"),
    ("group.sibling.rfield-10", "None"),
    ######################################################################
    ## Spouse Options
    ######################################################################
    ("group.spouse.event-format", 1),
    ("group.spouse.show-age", True),
    ("group.spouse.sex-mode", 1),
    ("group.spouse.image-mode", 0),
    ("group.spouse.lfield-skip-birth-alternates", True),
    ("group.spouse.lfield-skip-death-alternates", True),
    ("group.spouse.lfield-1", "Event:Birth"),
    ("group.spouse.lfield-2", "Event:Baptism"),
    ("group.spouse.lfield-3", "Event:Christening"),
    ("group.spouse.lfield-4", "Event:Death"),
    ("group.spouse.lfield-5", "Event:Cremation"),
    ("group.spouse.lfield-6", "Event:Burial"),
    ("group.spouse.lfield-7", "None"),
    ("group.spouse.lfield-8", "None"),
    ("group.spouse.lfield-9", "None"),
    ("group.spouse.lfield-10", "None"),
    ("group.spouse.rfield-show-labels", False),
    ("group.spouse.rfield-1", "None"),
    ("group.spouse.rfield-2", "None"),
    ("group.spouse.rfield-3", "None"),
    ("group.spouse.rfield-4", "None"),
    ("group.spouse.rfield-5", "None"),
    ("group.spouse.rfield-6", "None"),
    ("group.spouse.rfield-7", "None"),
    ("group.spouse.rfield-8", "None"),
    ("group.spouse.rfield-9", "None"),
    ("group.spouse.rfield-10", "None"),
    ######################################################################
    ## Child Options
    ######################################################################
    ("group.child.event-format", 1),
    ("group.child.show-age", True),
    ("group.child.sex-mode", 1),
    ("group.child.image-mode", 0),
    ("group.child.number-children", True),
    ("group.child.reference-mode", 0),
    ("group.child.lfield-skip-birth-alternates", True),
    ("group.child.lfield-skip-death-alternates", True),
    ("group.child.lfield-1", "Event:Birth"),
    ("group.child.lfield-2", "Event:Baptism"),
    ("group.child.lfield-3", "Event:Christening"),
    ("group.child.lfield-4", "Event:Death"),
    ("group.child.lfield-5", "Event:Cremation"),
    ("group.child.lfield-6", "Event:Burial"),
    ("group.child.lfield-7", "None"),
    ("group.child.lfield-8", "None"),
    ("group.child.lfield-9", "None"),
    ("group.child.lfield-10", "None"),
    ("group.child.rfield-show-labels", False),
    ("group.child.rfield-1", "None"),
    ("group.child.rfield-2", "None"),
    ("group.child.rfield-3", "None"),
    ("group.child.rfield-4", "None"),
    ("group.child.rfield-5", "None"),
    ("group.child.rfield-6", "None"),
    ("group.child.rfield-7", "None"),
    ("group.child.rfield-8", "None"),
    ("group.child.rfield-9", "None"),
    ("group.child.rfield-10", "None"),
    ######################################################################
    ## Association Options
    ######################################################################
    ("group.association.event-format", 1),
    ("group.association.show-age", True),
    ("group.association.sex-mode", 1),
    ("group.association.image-mode", 0),
    ("group.association.reference-mode", 0),
    ("group.association.lfield-skip-birth-alternates", True),
    ("group.association.lfield-skip-death-alternates", True),
    ("group.association.lfield-1", "Event:Birth"),
    ("group.association.lfield-2", "Event:Baptism"),
    ("group.association.lfield-3", "Event:Christening"),
    ("group.association.lfield-4", "Event:Death"),
    ("group.association.lfield-5", "Event:Cremation"),
    ("group.association.lfield-6", "Event:Burial"),
    ("group.association.lfield-7", "None"),
    ("group.association.lfield-8", "None"),
    ("group.association.lfield-9", "None"),
    ("group.association.lfield-10", "None"),
    ("group.association.rfield-show-labels", False),
    ("group.association.rfield-1", "None"),
    ("group.association.rfield-2", "None"),
    ("group.association.rfield-3", "None"),
    ("group.association.rfield-4", "None"),
    ("group.association.rfield-5", "None"),
    ("group.association.rfield-6", "None"),
    ("group.association.rfield-7", "None"),
    ("group.association.rfield-8", "None"),
    ("group.association.rfield-9", "None"),
    ("group.association.rfield-10", "None"),
    ######################################################################
    ## Name Options
    ######################################################################
    ("group.name.show-age", False),
    ######################################################################
    ## Address Options
    ######################################################################
    ("group.address.show-age", False),
    ######################################################################
    ## Family Options
    ######################################################################
    ("group.family.event-format", 1),
    ("group.family.image-mode", 0),
    ("group.family.compact-mode", True),
    ("group.family.lfield-skip-marriage-alternates", True),
    ("group.family.lfield-skip-divorce-alternates", True),
    ("group.family.lfield-1", "Event:Marriage Banns"),
    ("group.family.lfield-2", "Event:Marriage"),
    ("group.family.lfield-3", "Event:Divorce"),
    ("group.family.lfield-4", "None"),
    ("group.family.lfield-5", "None"),
    ("group.family.lfield-6", "None"),
    ("group.family.lfield-7", "None"),
    ("group.family.lfield-8", "None"),
    ("group.family.lfield-9", "None"),
    ("group.family.lfield-10", "None"),
    ("group.family.rfield-show-labels", False),
    ("group.family.rfield-1", "None"),
    ("group.family.rfield-2", "None"),
    ("group.family.rfield-3", "None"),
    ("group.family.rfield-4", "None"),
    ("group.family.rfield-5", "None"),
    ("group.family.rfield-6", "None"),
    ("group.family.rfield-7", "None"),
    ("group.family.rfield-8", "None"),
    ("group.family.rfield-9", "None"),
    ("group.family.rfield-10", "None"),
    ######################################################################
    ## Event Options
    ######################################################################
    ("group.event.max-per-group", 300),
    ("group.event.event-format", 1),
    ("group.event.show-age", False),
    ("group.event.image-mode", 0),
    ("group.event.reference-mode", 0),
    ("group.event.color-scheme", 1),
    ("group.event.rfield-show-labels", False),
    ("group.event.rfield-1", "None"),
    ("group.event.rfield-2", "None"),
    ("group.event.rfield-3", "None"),
    ("group.event.rfield-4", "None"),
    ("group.event.rfield-5", "None"),
    ("group.event.show-description", False),
    ("group.event.show-participants", False),
    ("group.event.show-role-always", False),
    ("group.event.show-source-count", False),
    ("group.event.show-citation-count", False),
    ("group.event.show-best-confidence", False),
    ######################################################################
    ## Ordinance Options
    ######################################################################
    ("group.ldsord.show-age", False),
    ######################################################################
    ## Place Options
    ######################################################################
    ("group.place.max-per-group", 200),
    ("group.place.image-mode", 0),
    ("group.place.reference-mode", 1),
    ("group.place.show-all-enclosed-places", False),
    ######################################################################
    ## Citation Options
    ######################################################################
    ("group.citation.max-per-group", 200),
    ("group.citation.image-mode", 0),
    ("group.citation.show-age", False),
    ("group.citation.sort-by-date", False),
    ("group.citation.include-indirect", True),
    ("group.citation.include-parent-family", True),
    ("group.citation.include-family", True),
    ("group.citation.include-family-indirect", True),
    ("group.citation.show-date", True),
    ("group.citation.show-publisher", True),
    ("group.citation.show-reference-type", False),
    ("group.citation.show-reference-description", False),
    ("group.citation.show-confidence", False),
    ("group.citation.rfield-show-labels", False),
    ("group.citation.rfield-1", "None"),
    ("group.citation.rfield-2", "None"),
    ("group.citation.rfield-3", "None"),
    ("group.citation.rfield-4", "None"),
    ("group.citation.rfield-5", "None"),
    ######################################################################
    ## Source Options
    ######################################################################
    ("group.source.max-per-group", 200),
    ("group.source.event-format", 1),
    ("group.source.image-mode", 0),
    ("group.source.rfield-show-labels", False),
    ("group.source.rfield-1", "None"),
    ("group.source.rfield-2", "None"),
    ("group.source.rfield-3", "None"),
    ("group.source.rfield-4", "None"),
    ("group.source.rfield-5", "None"),
    ######################################################################
    ## Repository Options
    ######################################################################
    ("group.repository.reference-mode", 1),
    ("group.repository.show-call-number", True),
    ("group.repository.show-media-type", True),
    ("group.repository.show-repository-type", True),
    ######################################################################
    ## Media Options
    ######################################################################
    ("group.media.max-per-group", 200),
    ("group.media.show-age", False),
    ("group.media.sort-by-date", False),
    ("group.media.group-by-type", False),
    ("group.media.filter-non-photos", False),
    ("group.media.image-mode", 2),
    ("group.media.reference-mode", 1),
    ("group.media.show-date", True),
    ("group.media.show-path", True),
    ("group.media.show-mime-type", True),
    ("group.media.rfield-show-labels", False),
    ("group.media.rfield-1", "None"),
    ("group.media.rfield-2", "None"),
    ("group.media.rfield-3", "None"),
    ("group.media.rfield-4", "None"),
    ("group.media.rfield-5", "None"),
    ######################################################################
    ## Note Options
    ######################################################################
    ("group.note.max-per-group", 200),
    ("group.note.text-on-top", False),
    ("group.note.preview-mode", True),
    ("group.note.preview-lines", 3),
    ("group.note.include-child-objects", True),
    ######################################################################
    # Timeline Options
    #
    ######################################################################
    ## Person Timeline
    ######################################################################
    ("timeline.person.image-mode", 0),
    ("timeline.person.reference-mode", 0),
    ("timeline.person.color-scheme", 1),
    ("timeline.person.include-media", False),
    ("timeline.person.include-names", False),
    ("timeline.person.include-addresses", False),
    ("timeline.person.include-ldsords", False),
    ("timeline.person.include-citations", False),
    ("timeline.person.show-description", False),
    ("timeline.person.show-participants", False),
    ("timeline.person.show-role-always", False),
    ("timeline.person.show-source-count", False),
    ("timeline.person.show-citation-count", False),
    ("timeline.person.show-best-confidence", False),
    ("timeline.person.show-age", True),
    ("timeline.person.rfield-show-labels", False),
    ("timeline.person.rfield-1", "None"),
    ("timeline.person.rfield-2", "None"),
    ("timeline.person.rfield-3", "None"),
    ("timeline.person.rfield-4", "None"),
    ("timeline.person.rfield-5", "None"),
    ("timeline.person.show-class-vital", True),
    ("timeline.person.show-class-family", True),
    ("timeline.person.show-class-religious", True),
    ("timeline.person.show-class-vocational", True),
    ("timeline.person.show-class-academic", True),
    ("timeline.person.show-class-travel", True),
    ("timeline.person.show-class-legal", True),
    ("timeline.person.show-class-residence", True),
    ("timeline.person.show-class-other", True),
    ("timeline.person.show-class-custom", True),
    ("timeline.person.generations-ancestors", 1),
    ("timeline.person.generations-offspring", 1),
    ("timeline.person.show-family-father", True),
    ("timeline.person.show-family-mother", True),
    ("timeline.person.show-family-brother", True),
    ("timeline.person.show-family-sister", True),
    ("timeline.person.show-family-wife", True),
    ("timeline.person.show-family-husband", True),
    ("timeline.person.show-family-son", True),
    ("timeline.person.show-family-daughter", True),
    ("timeline.person.show-family-class-vital", False),
    ("timeline.person.show-family-class-family", False),
    ("timeline.person.show-family-class-religious", False),
    ("timeline.person.show-family-class-vocational", False),
    ("timeline.person.show-family-class-academic", False),
    ("timeline.person.show-family-class-travel", False),
    ("timeline.person.show-family-class-legal", False),
    ("timeline.person.show-family-class-residence", False),
    ("timeline.person.show-family-class-other", False),
    ("timeline.person.show-family-class-custom", False),
    ######################################################################
    ## Family Timeline
    ######################################################################
    ("timeline.family.image-mode", 0),
    ("timeline.family.reference-mode", 0),
    ("timeline.family.color-scheme", 1),
    ("timeline.family.include-media", False),
    ("timeline.family.include-ldsords", False),
    ("timeline.family.include-citations", False),
    ("timeline.family.show-description", False),
    ("timeline.family.show-participants", False),
    ("timeline.family.show-role-always", False),
    ("timeline.family.show-source-count", False),
    ("timeline.family.show-citation-count", False),
    ("timeline.family.show-best-confidence", False),
    ("timeline.family.show-age", True),
    ("timeline.family.rfield-show-labels", False),
    ("timeline.family.rfield-1", "None"),
    ("timeline.family.rfield-2", "None"),
    ("timeline.family.rfield-3", "None"),
    ("timeline.family.rfield-4", "None"),
    ("timeline.family.rfield-5", "None"),
    ("timeline.family.show-class-vital", True),
    ("timeline.family.show-class-family", True),
    ("timeline.family.show-class-religious", True),
    ("timeline.family.show-class-vocational", True),
    ("timeline.family.show-class-academic", True),
    ("timeline.family.show-class-travel", True),
    ("timeline.family.show-class-legal", True),
    ("timeline.family.show-class-residence", True),
    ("timeline.family.show-class-other", True),
    ("timeline.family.show-class-custom", True),
    ######################################################################
    ## Place Timeline
    ######################################################################
    ("timeline.place.image-mode", 0),
    ("timeline.place.reference-mode", 3),
    ("timeline.place.color-scheme", 0),
    ("timeline.place.include-media", True),
    ("timeline.place.include-citations", True),
    ("timeline.place.show-description", True),
    ("timeline.place.show-participants", True),
    ("timeline.place.show-role-always", False),
    ("timeline.place.show-source-count", True),
    ("timeline.place.show-citation-count", True),
    ("timeline.place.show-best-confidence", True),
    ("timeline.place.show-age", True),
    ("timeline.place.rfield-show-labels", False),
    ("timeline.place.rfield-1", "None"),
    ("timeline.place.rfield-2", "None"),
    ("timeline.place.rfield-3", "None"),
    ("timeline.place.rfield-4", "None"),
    ("timeline.place.rfield-5", "None"),
    ("timeline.place.show-class-vital", True),
    ("timeline.place.show-class-family", True),
    ("timeline.place.show-class-religious", True),
    ("timeline.place.show-class-vocational", True),
    ("timeline.place.show-class-academic", True),
    ("timeline.place.show-class-travel", True),
    ("timeline.place.show-class-legal", True),
    ("timeline.place.show-class-residence", True),
    ("timeline.place.show-class-other", True),
    ("timeline.place.show-class-custom", True),
    ######################################################################
    # Additional Color Schemes
    #
    ######################################################################
    ## Confidence Color Scheme
    ######################################################################
    ("colors.confidence.very-high", ["#bbe68a", "#304918"]),
    ("colors.confidence.high", ["#b8cee6", "#1f344a"]),
    ("colors.confidence.normal", ["#f3dbb6", "#75507b"]),
    ("colors.confidence.low", ["#feccf0", "#62242d"]),
    ("colors.confidence.very-low", ["#ffdede", "#5c3636"]),
    ("colors.confidence.border-very-high", ["#304918", "#bbe68a"]),
    ("colors.confidence.border-high", ["#1f4986", "#171d26"]),
    ("colors.confidence.border-normal", ["#8e5801", "#8e5801"]),
    ("colors.confidence.border-low", ["#861f69", "#261111"]),
    ("colors.confidence.border-very-low", ["#ff7373", "#720b0b"]),
    ######################################################################
    ## Relationship Color Scheme
    ######################################################################
    ("colors.relations.active", ["#bbe68e", "#304918"]),
    ("colors.relations.spouse", ["#bbe68e", "#304918"]),
    ("colors.relations.father", ["#feccf0", "#62242d"]),
    ("colors.relations.mother", ["#feccf0", "#62242d"]),
    ("colors.relations.brother", ["#f3dbb6", "#75507b"]),
    ("colors.relations.sister", ["#f3dbb6", "#75507b"]),
    ("colors.relations.son", ["#b8cee6", "#1f344a"]),
    ("colors.relations.daughter", ["#b8cee6", "#1f344a"]),
    ("colors.relations.none", ["#ffdede", "#5c3636"]),
    ("colors.relations.border-active", ["#304918", "#bbe68a"]),
    ("colors.relations.border-spouse", ["#304918", "#bbe68a"]),
    ("colors.relations.border-father", ["#861f69", "#261111"]),
    ("colors.relations.border-mother", ["#861f69", "#261111"]),
    ("colors.relations.border-brother", ["#8e5801", "#8e5801"]),
    ("colors.relations.border-sister", ["#8e5801", "#8e5801"]),
    ("colors.relations.border-son", ["#1f4986", "#171d26"]),
    ("colors.relations.border-daughter", ["#1f4986", "#171d26"]),
    ("colors.relations.border-none", ["#ff7373", "#720b0b"]),
    ######################################################################
    ## Event Category Color Scheme
    ######################################################################
    ("colors.events.vital", ["#bbe68e", "#304918"]),
    ("colors.events.family", ["#b8cee6", "#1f344a"]),
    ("colors.events.religious", ["#bbe68e", "#304918"]),
    ("colors.events.vocational", ["#feccf0", "#62242d"]),
    ("colors.events.academic", ["#feccf0", "#62242d"]),
    ("colors.events.travel", ["#f3dbb6", "#75507b"]),
    ("colors.events.legal", ["#f3dbb6", "#75507b"]),
    ("colors.events.residence", ["#f3dbb6", "#75507b"]),
    ("colors.events.other", ["#ffdede", "#5c3636"]),
    ("colors.events.custom", ["#eeeeee", "#454545"]),
    ("colors.events.border-vital", ["#304918", "#bbe68a"]),
    ("colors.events.border-family", ["#1f4986", "#171d26"]),
    ("colors.events.border-religious", ["#304918", "#bbe68a"]),
    ("colors.events.border-vocational", ["#861f69", "#261111"]),
    ("colors.events.border-academic", ["#861f69", "#261111"]),
    ("colors.events.border-travel", ["#8e5801", "#8e5801"]),
    ("colors.events.border-legal", ["#8e5801", "#8e5801"]),
    ("colors.events.border-residence", ["#8e5801", "#8e5801"]),
    ("colors.events.border-other", ["#ff7373", "#720b0b"]),
    ("colors.events.border-custom", ["#cccccc", "#252525"]),
    ######################################################################
    ## Event Role Color Scheme
    ######################################################################
    ("colors.roles.primary", ["#bbe68e", "#304918"]),
    ("colors.roles.secondary", ["#f3dbb6", "#75507b"]),
    ("colors.roles.family", ["#b8cee6", "#1f344a"]),
    ("colors.roles.implicit", ["#eeeeee", "#454545"]),
    ("colors.roles.unknown", ["#ffdede", "#5c3636"]),
    ("colors.roles.border-primary", ["#304918", "#bbe68a"]),
    ("colors.roles.border-secondary", ["#8e5801", "#8e5801"]),
    ("colors.roles.border-family", ["#1f4986", "#171d26"]),
    ("colors.roles.border-implicit", ["#cccccc", "#252525"]),
    ("colors.roles.border-unknown", ["#ff7373", "#720b0b"]),
    ######################################################################
    # Page Layout Options
    #
    ######################################################################
    ## Name Page Options
    ######################################################################
    ("layout.name.tabbed", False),
    ("layout.name.scrolled", False),
    ("layout.name.groups", "citation,note,url"),
    ("layout.name.citation.visible", True),
    ("layout.name.citation.append", False),
    ("layout.name.note.visible", True),
    ("layout.name.note.append", False),
    ("layout.name.url.visible", True),
    ("layout.name.url.append", False),
    ######################################################################
    ## Attribute Page Options
    ######################################################################
    ("layout.attribute.tabbed", False),
    ("layout.attribute.scrolled", False),
    ("layout.attribute.groups", "citation,note,url"),
    ("layout.attribute.citation.visible", True),
    ("layout.attribute.citation.append", False),
    ("layout.attribute.note.visible", True),
    ("layout.attribute.note.append", False),
    ("layout.attribute.url.visible", True),
    ("layout.attribute.url.append", False),
    ######################################################################
    ## Address Page Options
    ######################################################################
    ("layout.address.tabbed", False),
    ("layout.address.scrolled", False),
    ("layout.address.groups", "citation,note,url"),
    ("layout.address.citation.visible", True),
    ("layout.address.citation.append", False),
    ("layout.address.note.visible", True),
    ("layout.address.note.append", False),
    ("layout.address.url.visible", True),
    ("layout.address.url.append", False),
    ######################################################################
    ## ChildRef Page Options
    ######################################################################
    ("layout.childref.tabbed", False),
    ("layout.childref.scrolled", False),
    ("layout.childref.groups", "citation,note,url"),
    ("layout.childref.citation.visible", True),
    ("layout.childref.citation.append", False),
    ("layout.childref.note.visible", True),
    ("layout.childref.note.append", False),
    ("layout.childref.url.visible", True),
    ("layout.childref.url.append", False),
    ######################################################################
    ## PersonRef Page Options
    ######################################################################
    ("layout.personref.tabbed", False),
    ("layout.personref.scrolled", False),
    ("layout.personref.groups", "citation,note,url"),
    ("layout.personref.citation.visible", True),
    ("layout.personref.citation.append", False),
    ("layout.personref.note.visible", True),
    ("layout.personref.note.append", False),
    ("layout.personref.url.visible", True),
    ("layout.personref.url.append", False),
    ######################################################################
    ## Person Page Options
    ######################################################################
    ("layout.person.tabbed", False),
    ("layout.person.scrolled", False),
    (
        "layout.person.groups",
        "paternal,maternal,parent,event,timeline,ldsord,spouse,name,"
        "attribute,association,citation,address,url,note,media,reference,"
        "uncited,todo,research",
    ),
    ("layout.person.paternal.visible", False),
    ("layout.person.paternal.append", False),
    ("layout.person.maternal.visible", False),
    ("layout.person.maternal.append", False),
    ("layout.person.parent.visible", True),
    ("layout.person.parent.append", False),
    ("layout.person.event.visible", False),
    ("layout.person.event.append", False),
    ("layout.person.timeline.visible", True),
    ("layout.person.timeline.append", False),
    ("layout.person.ldsord.visible", False),
    ("layout.person.ldsord.append", False),
    ("layout.person.spouse.visible", True),
    ("layout.person.spouse.append", False),
    ("layout.person.name.visible", False),
    ("layout.person.name.append", False),
    ("layout.person.attribute.visible", False),
    ("layout.person.attribute.append", False),
    ("layout.person.association.visible", False),
    ("layout.person.association.append", False),
    ("layout.person.citation.visible", True),
    ("layout.person.citation.append", False),
    ("layout.person.address.visible", False),
    ("layout.person.address.append", False),
    ("layout.person.url.visible", False),
    ("layout.person.url.append", False),
    ("layout.person.note.visible", False),
    ("layout.person.note.append", False),
    ("layout.person.media.visible", False),
    ("layout.person.media.append", False),
    ("layout.person.reference.visible", False),
    ("layout.person.reference.append", False),
    ("layout.person.uncited.visible", False),
    ("layout.person.uncited.append", False),
    ("layout.person.todo.visible", False),
    ("layout.person.todo.append", False),
    ("layout.person.research.visible", False),
    ("layout.person.research.append", False),
    ######################################################################
    ## Family Page Options
    ######################################################################
    ("layout.family.tabbed", False),
    ("layout.family.scrolled", False),
    (
        "layout.family.groups",
        "child,event,timeline,ldsord,attribute,citation,url,note,media,"
        "reference,uncited,todo,research",
    ),
    ("layout.family.child.visible", True),
    ("layout.family.child.append", False),
    ("layout.family.event.visible", False),
    ("layout.family.event.append", False),
    ("layout.family.timeline.visible", True),
    ("layout.family.timeline.append", False),
    ("layout.family.ldsord.visible", False),
    ("layout.family.ldsord.append", False),
    ("layout.family.attribute.visible", False),
    ("layout.family.attribute.append", False),
    ("layout.family.citation.visible", True),
    ("layout.family.citation.append", False),
    ("layout.family.url.visible", False),
    ("layout.family.url.append", False),
    ("layout.family.note.visible", False),
    ("layout.family.note.append", False),
    ("layout.family.media.visible", False),
    ("layout.family.media.append", False),
    ("layout.family.reference.visible", False),
    ("layout.family.reference.append", False),
    ("layout.family.uncited.visible", False),
    ("layout.family.uncited.append", False),
    ("layout.family.todo.visible", False),
    ("layout.family.todo.append", False),
    ("layout.family.research.visible", False),
    ("layout.family.research.append", False),
    ######################################################################
    ## Event Page Options
    ######################################################################
    ("layout.event.tabbed", False),
    ("layout.event.scrolled", False),
    (
        "layout.event.groups",
        "attribute,people,family,citation,url,note,media,reference,"
        "todo,research",
    ),
    ("layout.event.attribute.visible", False),
    ("layout.event.attribute.append", False),
    ("layout.event.people.visible", True),
    ("layout.event.people.append", False),
    ("layout.event.family.visible", True),
    ("layout.event.family.append", False),
    ("layout.event.citation.visible", True),
    ("layout.event.citation.append", False),
    ("layout.event.url.visible", False),
    ("layout.event.url.append", False),
    ("layout.event.note.visible", False),
    ("layout.event.note.append", False),
    ("layout.event.media.visible", False),
    ("layout.event.media.append", False),
    ("layout.event.reference.visible", False),
    ("layout.event.reference.append", False),
    ("layout.event.todo.visible", False),
    ("layout.event.todo.append", False),
    ("layout.event.research.visible", False),
    ("layout.event.research.append", False),
    ######################################################################
    ## EventRef Page Options
    ######################################################################
    ("layout.eventref.tabbed", False),
    ("layout.eventref.scrolled", False),
    ("layout.eventref.groups", "attribute,note,url"),
    ("layout.eventref.attribute.visible", True),
    ("layout.eventref.attribute.append", False),
    ("layout.eventref.note.visible", True),
    ("layout.eventref.note.append", False),
    ("layout.eventref.url.visible", True),
    ("layout.eventref.url.append", False),
    ######################################################################
    ## LdsOrd Page Options
    ######################################################################
    ("layout.ldsord.tabbed", False),
    ("layout.ldsord.scrolled", False),
    (
        "layout.ldsord.groups",
        "citation,url,note",
    ),
    ("layout.ldsord.citation.visible", True),
    ("layout.ldsord.citation.append", False),
    ("layout.ldsord.url.visible", True),
    ("layout.ldsord.url.append", True),
    ("layout.ldsord.note.visible", True),
    ("layout.ldsord.note.append", False),
    ######################################################################
    ## Source Page Options
    ######################################################################
    ("layout.source.tabbed", False),
    ("layout.source.scrolled", False),
    (
        "layout.source.groups",
        "repository,media,citation,people,event,place,url,note,"
        "attribute,reference",
    ),
    ("layout.source.repository.visible", True),
    ("layout.source.repository.append", True),
    ("layout.source.citation.visible", True),
    ("layout.source.citation.append", False),
    ("layout.source.attribute.visible", False),
    ("layout.source.attribute.append", False),
    ("layout.source.url.visible", True),
    ("layout.source.url.append", True),
    ("layout.source.note.visible", True),
    ("layout.source.note.append", False),
    ("layout.source.people.visible", True),
    ("layout.source.people.append", True),
    ("layout.source.event.visible", True),
    ("layout.source.event.append", False),
    ("layout.source.place.visible", True),
    ("layout.source.place.append", False),
    ("layout.source.media.visible", True),
    ("layout.source.media.append", False),
    ("layout.source.reference.visible", False),
    ("layout.source.reference.append", False),
    ######################################################################
    ## Citation Page Options
    ######################################################################
    ("layout.citation.tabbed", False),
    ("layout.citation.scrolled", False),
    (
        "layout.citation.groups",
        "reference,attribute,url,note,media",
    ),
    ("layout.citation.reference.visible", True),
    ("layout.citation.reference.append", False),
    ("layout.citation.attribute.visible", False),
    ("layout.citation.attribute.append", False),
    ("layout.citation.url.visible", True),
    ("layout.citation.url.append", True),
    ("layout.citation.note.visible", True),
    ("layout.citation.note.append", False),
    ("layout.citation.media.visible", True),
    ("layout.citation.media.append", False),
    ######################################################################
    ## Repository Page Options
    ######################################################################
    ("layout.repository.tabbed", False),
    ("layout.repository.scrolled", False),
    ("layout.repository.groups", "reference,source,url,note"),
    ("layout.repository.source.visible", True),
    ("layout.repository.source.append", False),
    ("layout.repository.url.visible", True),
    ("layout.repository.url.append", True),
    ("layout.repository.note.visible", True),
    ("layout.repository.note.append", False),
    ("layout.repository.reference.visible", True),
    ("layout.repository.reference.append", False),
    ######################################################################
    ## RepoRef Page Options
    ######################################################################
    ("layout.reporef.tabbed", False),
    ("layout.reporef.scrolled", False),
    ("layout.reporef.groups", "note,url"),
    ("layout.reporef.note.visible", True),
    ("layout.reporef.note.append", False),
    ("layout.reporef.url.visible", True),
    ("layout.reporef.url.append", False),
    ######################################################################
    ## Note Page Options
    ######################################################################
    ("layout.note.tabbed", False),
    ("layout.note.scrolled", False),
    ("layout.note.groups", "reference"),
    ("layout.note.reference.visible", True),
    ("layout.note.reference.append", False),
    ######################################################################
    ## Media Page Options
    ######################################################################
    ("layout.media.tabbed", False),
    ("layout.media.scrolled", False),
    (
        "layout.media.groups",
        "reference,citation,attribute,url,note",
    ),
    ("layout.media.citation.visible", True),
    ("layout.media.citation.append", False),
    ("layout.media.attribute.visible", False),
    ("layout.media.attribute.append", False),
    ("layout.media.url.visible", True),
    ("layout.media.url.append", True),
    ("layout.media.note.visible", True),
    ("layout.media.note.append", False),
    ("layout.media.reference.visible", True),
    ("layout.media.reference.append", False),
    ######################################################################
    ## MediaRef Page Options
    ######################################################################
    ("layout.mediaref.tabbed", False),
    ("layout.mediaref.scrolled", False),
    ("layout.mediaref.groups", "attribute,citation,note,url"),
    ("layout.mediaref.attribute.visible", True),
    ("layout.mediaref.attribute.append", False),
    ("layout.mediaref.citation.visible", True),
    ("layout.mediaref.citation.append", False),
    ("layout.mediaref.note.visible", True),
    ("layout.mediaref.note.append", False),
    ("layout.mediaref.url.visible", True),
    ("layout.mediaref.url.append", False),
    ######################################################################
    ## Place Page Options
    ######################################################################
    ("layout.place.tabbed", False),
    ("layout.place.scrolled", False),
    (
        "layout.place.groups",
        "timeline,enclosing,enclosed,media,citation,url,note,reference",
    ),
    ("layout.place.timeline.visible", True),
    ("layout.place.timeline.append", False),
    ("layout.place.enclosing.visible", True),
    ("layout.place.enclosing.append", True),
    ("layout.place.enclosed.visible", True),
    ("layout.place.enclosed.append", False),
    ("layout.place.media.visible", True),
    ("layout.place.media.append", False),
    ("layout.place.citation.visible", True),
    ("layout.place.citation.append", False),
    ("layout.place.url.visible", True),
    ("layout.place.url.append", True),
    ("layout.place.note.visible", True),
    ("layout.place.note.append", False),
    ("layout.place.reference.visible", False),
    ("layout.place.reference.append", False),
    ######################################################################
    ## Tag Page Options
    ######################################################################
    ("layout.tag.tabbed", False),
    ("layout.tag.scrolled", False),
    (
        "layout.tag.groups",
        "person,family,event,place,citation,source,repository,note,media",
    ),
    ("layout.tag.person.visible", True),
    ("layout.tag.person.append", True),
    ("layout.tag.family.visible", True),
    ("layout.tag.family.append", False),
    ("layout.tag.event.visible", True),
    ("layout.tag.event.append", True),
    ("layout.tag.place.visible", True),
    ("layout.tag.place.append", False),
    ("layout.tag.citation.visible", True),
    ("layout.tag.citation.append", True),
    ("layout.tag.source.visible", True),
    ("layout.tag.source.append", True),
    ("layout.tag.repository.visible", True),
    ("layout.tag.repository.append", False),
    ("layout.tag.note.visible", True),
    ("layout.tag.note.append", True),
    ("layout.tag.media.visible", True),
    ("layout.tag.media.append", False),
    ######################################################################
    ## Statistics Page Options
    ######################################################################
    ("layout.statistics.tabbed", False),
    ("layout.statistics.scrolled", False),
    (
        "layout.statistics.groups",
        "stats-person,stats-family,stats-child,stats-association,stats-event,"
        "stats-ldsordperson,stats-ldsordfamily,stats-participant,stats-place,"
        "stats-media,stats-note,stats-tag,stats-bookmark,stats-repository,"
        "stats-source,stats-citation,stats-uncited,stats-privacy",
    ),
    ("layout.statistics.stats-person.visible", True),
    ("layout.statistics.stats-person.append", True),
    ("layout.statistics.stats-family.visible", True),
    ("layout.statistics.stats-family.append", True),
    ("layout.statistics.stats-child.visible", True),
    ("layout.statistics.stats-child.append", True),
    ("layout.statistics.stats-association.visible", True),
    ("layout.statistics.stats-association.append", False),
    ("layout.statistics.stats-event.visible", True),
    ("layout.statistics.stats-event.append", True),
    ("layout.statistics.stats-ldsordperson.visible", True),
    ("layout.statistics.stats-ldsordperson.append", True),
    ("layout.statistics.stats-ldsordfamily.visible", True),
    ("layout.statistics.stats-ldsordfamily.append", True),
    ("layout.statistics.stats-participant.visible", True),
    ("layout.statistics.stats-participant.append", False),
    ("layout.statistics.stats-place.visible", False),
    ("layout.statistics.stats-place.append", True),
    ("layout.statistics.stats-media.visible", False),
    ("layout.statistics.stats-media.append", True),
    ("layout.statistics.stats-note.visible", False),
    ("layout.statistics.stats-note.append", True),
    ("layout.statistics.stats-tag.visible", False),
    ("layout.statistics.stats-tag.append", True),
    ("layout.statistics.stats-bookmark.visible", False),
    ("layout.statistics.stats-bookmark.append", False),
    ("layout.statistics.stats-repository.visible", True),
    ("layout.statistics.stats-repository.append", True),
    ("layout.statistics.stats-source.visible", True),
    ("layout.statistics.stats-source.append", True),
    ("layout.statistics.stats-citation.visible", True),
    ("layout.statistics.stats-citation.append", False),
    ("layout.statistics.stats-uncited.visible", True),
    ("layout.statistics.stats-uncited.append", True),
    ("layout.statistics.stats-privacy.visible", True),
    ("layout.statistics.stats-privacy.append", True),
    ######################################################################
    # Miscellaneous Options
    ######################################################################
    ("status.todo", False),
    ("status.citation-alert", False),
    ("status.confidence-ranking", False),
)


def load_on_reg(_dummy_dbstate, _dummy_uistate, _dummy_plugin):
    """
    Return template option set.
    """
    return [{"name": "Minimal", "options": _TEMPLATE}]
