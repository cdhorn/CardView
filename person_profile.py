# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackermann
# Copyright (C) 2009-2010  Gary Burton
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2015-2016  Nick Hall
# Copyright (C) 2015       Serge Noiraud
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
Person Profile View
"""

# -------------------------------------------------------------------------
#
# Set up logging
#
# -------------------------------------------------------------------------
import logging
_LOG = logging.getLogger("plugin.relview")


# -------------------------------------------------------------------------
#
# GTK/Gnome modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk, Gdk


# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.const import CUSTOM_FILTERS
from gramps.gen.datehandler import displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.errors import WindowActiveError
from gramps.gen.lib import Person
from gramps.gui.editors import FilterEditor
from gramps.gui.uimanager import ActionGroup
from gramps.gui.views.bookmarks import PersonBookmarks
from gramps.gui.views.navigationview import NavigationView
from gramps.gui.widgets.reorderfam import Reorder
from gramps.gui.widgets import BasicLabel

_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored

_NAME_START = 0
_LABEL_START = 0
_LABEL_STOP = 1
_DATA_START = _LABEL_STOP
_DATA_STOP = _DATA_START + 1
_BTN_START = _DATA_STOP
_BTN_STOP = _BTN_START + 2
_PLABEL_START = 1
_PLABEL_STOP = _PLABEL_START + 1
_PDATA_START = _PLABEL_STOP
_PDATA_STOP = _PDATA_START + 2
_PDTLS_START = _PLABEL_STOP
_PDTLS_STOP = _PDTLS_START + 2
_CLABEL_START = _PLABEL_START + 1
_CLABEL_STOP = _CLABEL_START + 1
_CDATA_START = _CLABEL_STOP
_CDATA_STOP = _CDATA_START + 1
_CDTLS_START = _CDATA_START
_CDTLS_STOP = _CDTLS_START + 1
_ALABEL_START = 0
_ALABEL_STOP = _ALABEL_START + 1
_ADATA_START = _ALABEL_STOP
_ADATA_STOP = _ADATA_START + 3
_SDATA_START = 2
_SDATA_STOP = 4
_RETURN = Gdk.keyval_from_name("Return")
_KP_ENTER = Gdk.keyval_from_name("KP_Enter")
_SPACE = Gdk.keyval_from_name("space")
_LEFT_BUTTON = 1
_RIGHT_BUTTON = 3

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from frame_base import button_activated
from frame_groups import (
    get_parent_profiles,
    get_spouse_profiles,
    get_citation_profiles,
    get_timeline_profiles,
)
from frame_person import PersonGrampsFrame
from frame_utils import (
    EVENT_DISPLAY_MODES,
    IMAGE_DISPLAY_MODES,
    TAG_DISPLAY_MODES,
    TIMELINE_COLOR_MODES,
    AttributeSelector,
    FrameFieldSelector
)


class PersonProfileView(NavigationView):
    """
    Summary view of a person in a navigatable format.
    """

    CONFIGSETTINGS = (
        ("preferences.profile.person.layout.enable-tooltips", True),
        ("preferences.profile.person.layout.enable-warnings", True),
        ("preferences.profile.person.layout.pinned-header", True),
        ("preferences.profile.person.layout.spouses-left", True),
        ("preferences.profile.person.layout.families-stacked", False),
        ("preferences.profile.person.layout.show-timeline", True),
        ("preferences.profile.person.layout.show-citations", False),
        ("preferences.profile.person.layout.border-width", 2),
        ("preferences.profile.person.layout.use-color-scheme", True),
        ("preferences.profile.person.layout.use-smaller-detail-font", True),
        ("preferences.profile.person.layout.sort-tags-by-name", False),
        ("preferences.profile.person.layout.right-to-left", False),
        # active person
        ("preferences.profile.person.active.event-format", 1),
        ("preferences.profile.person.active.tag-format", 1),
        ("preferences.profile.person.active.tag-width", 10),
        ("preferences.profile.person.active.image-mode", 3),
        ("preferences.profile.person.active.show-gender", True),
        ("preferences.profile.person.active.show-age", True),
        ("preferences.profile.person.active.show-baptism", True),
        ("preferences.profile.person.active.show-burial", True),
        ("preferences.profile.person.active.show-relation", True),
        ("preferences.profile.person.active.facts-field-skip-birth-alternates", False),
        ("preferences.profile.person.active.facts-field-skip-death-alternates", False),
        ("preferences.profile.person.active.facts-field-1", "Event:Birth:False"),
        ("preferences.profile.person.active.facts-field-2", "Event:Baptism:False"),
        ("preferences.profile.person.active.facts-field-3", "Event:Christening:False"),
        ("preferences.profile.person.active.facts-field-4", "Event:Death:False"),
        ("preferences.profile.person.active.facts-field-5", "Event:Burial:False"),
        ("preferences.profile.person.active.facts-field-6", "Event:Cremation:False"),
        ("preferences.profile.person.active.facts-field-7", "Event:Probate:False"),
        ("preferences.profile.person.active.facts-field-8", "None"),
        ("preferences.profile.person.active.extra-field-skip-birth-alternates", False),
        ("preferences.profile.person.active.extra-field-skip-death-alternates", False),
        ("preferences.profile.person.active.extra-field-1", "None"),
        ("preferences.profile.person.active.extra-field-2", "None"),
        ("preferences.profile.person.active.extra-field-3", "None"),
        ("preferences.profile.person.active.extra-field-4", "None"),
        ("preferences.profile.person.active.extra-field-5", "None"),
        ("preferences.profile.person.active.extra-field-6", "None"),
        ("preferences.profile.person.active.extra-field-7", "None"),
        ("preferences.profile.person.active.extra-field-8", "None"),
        ("preferences.profile.person.active.metadata-attribute-1", "None"),
        ("preferences.profile.person.active.metadata-attribute-2", "None"),
        ("preferences.profile.person.active.metadata-attribute-3", "None"),
        ("preferences.profile.person.active.metadata-attribute-4", "None"),
        ("preferences.profile.person.active.metadata-attribute-5", "None"),
        ("preferences.profile.person.active.metadata-attribute-6", "None"),
        ("preferences.profile.person.active.metadata-attribute-7", "None"),
        ("preferences.profile.person.active.metadata-attribute-8", "None"),
        # parent
        ("preferences.profile.person.parent.event-format", 1),
        ("preferences.profile.person.parent.tag-format", 1),
        ("preferences.profile.person.parent.tag-width", 10),
        ("preferences.profile.person.parent.image-mode", 1),
        ("preferences.profile.person.parent.show-matrilineal", False),
        ("preferences.profile.person.parent.expand-children", True),
        ("preferences.profile.person.parent.show-gender", True),
        ("preferences.profile.person.parent.show-age", False),
        ("preferences.profile.person.parent.show-divorce", True),
        ("preferences.profile.person.parent.facts-field-skip-birth-alternates", True),
        ("preferences.profile.person.parent.facts-field-skip-death-alternates", True),
        ("preferences.profile.person.parent.facts-field-1", "Event:Birth:False"),
        ("preferences.profile.person.parent.facts-field-2", "Event:Baptism:False"),
        ("preferences.profile.person.parent.facts-field-3", "Event:Christening:False"),
        ("preferences.profile.person.parent.facts-field-4", "Event:Death:False"),
        ("preferences.profile.person.parent.facts-field-5", "Event:Burial:False"),
        ("preferences.profile.person.parent.facts-field-6", "Event:Cremation:False"),
        ("preferences.profile.person.parent.facts-field-7", "Event:Probate:False"),
        ("preferences.profile.person.parent.facts-field-8", "None"),
        ("preferences.profile.person.parent.metadata-attribute-1", "None"),
        ("preferences.profile.person.parent.metadata-attribute-2", "None"),
        ("preferences.profile.person.parent.metadata-attribute-3", "None"),
        ("preferences.profile.person.parent.metadata-attribute-4", "None"),
        ("preferences.profile.person.parent.metadata-attribute-5", "None"),
        ("preferences.profile.person.parent.metadata-attribute-6", "None"),
        ("preferences.profile.person.parent.metadata-attribute-7", "None"),
        ("preferences.profile.person.parent.metadata-attribute-8", "None"),
        # spouse
        ("preferences.profile.person.spouse.event-format", 1),
        ("preferences.profile.person.spouse.tag-format", 1),
        ("preferences.profile.person.spouse.tag-width", 10),
        ("preferences.profile.person.spouse.image-mode", 3),
        ("preferences.profile.person.spouse.expand-children", True),
        ("preferences.profile.person.spouse.show-spouse-only", True),
        ("preferences.profile.person.spouse.show-gender", True),
        ("preferences.profile.person.spouse.show-age", False),
        ("preferences.profile.person.spouse.show-divorce", True),
        ("preferences.profile.person.spouse.facts-field-skip-birth-alternates", True),
        ("preferences.profile.person.spouse.facts-field-skip-death-alternates", True),
        ("preferences.profile.person.spouse.facts-field-1", "Event:Birth:False"),
        ("preferences.profile.person.spouse.facts-field-2", "Event:Baptism:False"),
        ("preferences.profile.person.spouse.facts-field-3", "Event:Christening:False"),
        ("preferences.profile.person.spouse.facts-field-4", "Event:Death:False"),
        ("preferences.profile.person.spouse.facts-field-5", "Event:Burial:False"),
        ("preferences.profile.person.spouse.facts-field-6", "Event:Cremation:False"),
        ("preferences.profile.person.spouse.facts-field-7", "Event:Probate:False"),
        ("preferences.profile.person.spouse.facts-field-8", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-1", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-2", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-3", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-4", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-5", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-6", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-7", "None"),
        ("preferences.profile.person.spouse.metadata-attribute-8", "None"),
        # child
        ("preferences.profile.person.child.event-format", 1),
        ("preferences.profile.person.child.tag-format", 1),
        ("preferences.profile.person.child.tag-width", 10),
        ("preferences.profile.person.child.image-mode", 3),
        ("preferences.profile.person.child.number-children", True),
        ("preferences.profile.person.child.show-gender", True),
        ("preferences.profile.person.child.show-age", False),
        ("preferences.profile.person.child.facts-field-skip-birth-alternates", True),
        ("preferences.profile.person.child.facts-field-skip-death-alternates", True),
        ("preferences.profile.person.child.facts-field-1", "Event:Birth:False"),
        ("preferences.profile.person.child.facts-field-2", "Event:Baptism:False"),
        ("preferences.profile.person.child.facts-field-3", "Event:Christening:False"),
        ("preferences.profile.person.child.facts-field-4", "Event:Death:False"),
        ("preferences.profile.person.child.facts-field-5", "Event:Burial:False"),
        ("preferences.profile.person.child.facts-field-6", "Event:Cremation:False"),
        ("preferences.profile.person.child.facts-field-7", "Event:Probate:False"),
        ("preferences.profile.person.child.facts-field-8", "None"),
        ("preferences.profile.person.child.metadata-attribute-1", "None"),
        ("preferences.profile.person.child.metadata-attribute-2", "None"),
        ("preferences.profile.person.child.metadata-attribute-3", "None"),
        ("preferences.profile.person.child.metadata-attribute-4", "None"),
        ("preferences.profile.person.child.metadata-attribute-5", "None"),
        ("preferences.profile.person.child.metadata-attribute-6", "None"),
        ("preferences.profile.person.child.metadata-attribute-7", "None"),
        ("preferences.profile.person.child.metadata-attribute-8", "None"),
        # sibling
        ("preferences.profile.person.sibling.event-format", 1),
        ("preferences.profile.person.sibling.tag-format", 1),
        ("preferences.profile.person.sibling.tag-width", 10),
        ("preferences.profile.person.sibling.image-mode", 1),
        ("preferences.profile.person.sibling.number-children", True),
        ("preferences.profile.person.sibling.show-gender", True),
        ("preferences.profile.person.sibling.show-age", False),
        ("preferences.profile.person.sibling.facts-field-skip-birth-alternates", True),
        ("preferences.profile.person.sibling.facts-field-skip-death-alternates", True),
        ("preferences.profile.person.sibling.facts-field-1", "Event:Birth:False"),
        ("preferences.profile.person.sibling.facts-field-2", "Event:Baptism:False"),
        ("preferences.profile.person.sibling.facts-field-3", "Event:Christening:False"),
        ("preferences.profile.person.sibling.facts-field-4", "Event:Death:False"),
        ("preferences.profile.person.sibling.facts-field-5", "Event:Burial:False"),
        ("preferences.profile.person.sibling.facts-field-6", "Event:Cremation:False"),
        ("preferences.profile.person.sibling.facts-field-7", "Event:Probate:False"),
        ("preferences.profile.person.sibling.facts-field-8", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-1", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-2", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-3", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-4", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-5", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-6", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-7", "None"),
        ("preferences.profile.person.sibling.metadata-attribute-8", "None"),
        # timeline
        ("preferences.profile.person.timeline.tag-format", 1),
        ("preferences.profile.person.timeline.tag-width", 10),
        ("preferences.profile.person.timeline.image-mode", 1),
        ("preferences.profile.person.timeline.color-scheme", 1),
        ("preferences.profile.person.timeline.show-description", True),
        ("preferences.profile.person.timeline.show-participants", True),
        ("preferences.profile.person.timeline.show-role-always", False),
        ("preferences.profile.person.timeline.show-source-count", True),
        ("preferences.profile.person.timeline.show-citation-count", True),
        ("preferences.profile.person.timeline.show-best-confidence", True),
        ("preferences.profile.person.timeline.show-age", True),
        ("preferences.profile.person.timeline.show-class-vital", True),
        ("preferences.profile.person.timeline.show-class-family", True),
        ("preferences.profile.person.timeline.show-class-religious", True),
        ("preferences.profile.person.timeline.show-class-vocational", True),
        ("preferences.profile.person.timeline.show-class-academic", True),
        ("preferences.profile.person.timeline.show-class-travel", True),
        ("preferences.profile.person.timeline.show-class-legal", True),
        ("preferences.profile.person.timeline.show-class-residence", True),
        ("preferences.profile.person.timeline.show-class-other", True),
        ("preferences.profile.person.timeline.show-class-custom", True),
        ("preferences.profile.person.timeline.generations-ancestors", 1),
        ("preferences.profile.person.timeline.generations-offspring", 1),
        ("preferences.profile.person.timeline.show-family-father", True),
        ("preferences.profile.person.timeline.show-family-mother", True),
        ("preferences.profile.person.timeline.show-family-brother", True),
        ("preferences.profile.person.timeline.show-family-sister", True),
        ("preferences.profile.person.timeline.show-family-wife", True),
        ("preferences.profile.person.timeline.show-family-husband", True),
        ("preferences.profile.person.timeline.show-family-son", True),
        ("preferences.profile.person.timeline.show-family-daughter", True),
        ("preferences.profile.person.timeline.show-family-class-vital", False),
        ("preferences.profile.person.timeline.show-family-class-family", False),
        ("preferences.profile.person.timeline.show-family-class-religious", False),
        ("preferences.profile.person.timeline.show-family-class-vocational", False),
        ("preferences.profile.person.timeline.show-family-class-academic", False),
        ("preferences.profile.person.timeline.show-family-class-travel", False),
        ("preferences.profile.person.timeline.show-family-class-legal", False),
        ("preferences.profile.person.timeline.show-family-class-residence", False),
        ("preferences.profile.person.timeline.show-family-class-other", False),
        ("preferences.profile.person.timeline.show-family-class-custom", False),
        # citation
        ("preferences.profile.person.citation.tag-format", 1),
        ("preferences.profile.person.citation.tag-width", 10),
        ("preferences.profile.person.citation.image-mode", 1),
        ("preferences.profile.person.citation.sort-by-date", False),
        ("preferences.profile.person.citation.include-indirect", True),
        ("preferences.profile.person.citation.include-parent-family", True),
        ("preferences.profile.person.citation.include-family", True),
        ("preferences.profile.person.citation.include-family-indirect", True),
        ("preferences.profile.person.citation.show-date", True),
        ("preferences.profile.person.citation.show-publisher", True),
        ("preferences.profile.person.citation.show-reference-type", True),
        ("preferences.profile.person.citation.show-reference-description", True),
        ("preferences.profile.person.citation.show-confidence", True),
        # confidence color scheme
        ('preferences.profile.colors.confidence.very-high', ["#99c1f1","#304918"]),
        ('preferences.profile.colors.confidence.high', ["#8ff0a4","#454545"]),
        ('preferences.profile.colors.confidence.normal', ["#f9f06b","#454545"]),
        ('preferences.profile.colors.confidence.low', ["#ffbe6f","#454545"]),
        ('preferences.profile.colors.confidence.very-low', ["#f66161","#454545"]), 
        ('preferences.profile.colors.confidence.border-very-high', ["#1a5fb4","#000000"]),
        ('preferences.profile.colors.confidence.border-high', ["#26a269","#000000"]),
        ('preferences.profile.colors.confidence.border-normal', ["#e5a50a","#000000"]),
        ('preferences.profile.colors.confidence.border-low', ["#c64600","#000000"]),
        ('preferences.profile.colors.confidence.border-very-low', ["#a51d2d","#000000"]),
        # relation color scheme
        ('preferences.profile.colors.relations.active', ["#bbe68e","#304918"]),
        ('preferences.profile.colors.relations.spouse', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.father', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.mother', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.brother', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.sister', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.son', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.daughter', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.none', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.relations.border-active', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-spouse', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-father', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-mother', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-brother', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-sister', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-son', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-daughter', ["#cccccc","#000000"]),
        ('preferences.profile.colors.relations.border-none', ["#cccccc","#000000"]),
        # event category color scheme
        ('preferences.profile.colors.events.vital', ["#bbe68e","#304918"]),
        ('preferences.profile.colors.events.family', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.religious', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.vocational', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.academic', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.travel', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.legal', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.residence', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.other', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.custom', ["#eeeeee","#454545"]),
        ('preferences.profile.colors.events.border-vital', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-family', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-religious', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-vocational', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-academic', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-travel', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-legal', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-residence', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-other', ["#cccccc","#000000"]),
        ('preferences.profile.colors.events.border-custom', ["#cccccc","#000000"]),
    )

    def __init__(self, pdata, dbstate, uistate, nav_group=0):
        NavigationView.__init__(
            self,
            _("Person Profile"),
            pdata,
            dbstate,
            uistate,
            PersonBookmarks,
            nav_group,
        )
        dbstate.connect("database-changed", self.change_db)
        uistate.connect("nameformat-changed", self.build_tree)
        uistate.connect("placeformat-changed", self.build_tree)
        uistate.connect("font-changed", self.font_changed)
        uistate.connect("color", self.build_tree)
        self.redrawing = False

        self.child = None
        self.old_handle = None

        self.reorder_sensitive = False
        self.collapsed_items = {}

        self.additional_uis.append(self.additional_ui)

    def get_handle_from_gramps_id(self, gid):
        """
        Returns the handle of the specified object
        """
        obj = self.dbstate.db.get_person_from_gramps_id(gid)
        if obj:
            return obj.get_handle()
        return None

    def _connect_db_signals(self):
        """
        Implement from base class DbGUIElement
        Register the callbacks we need.
        """
        # Add a signal to pick up event changes, bug #1416
        self.callman.add_db_signal("event-update", self.redraw)
        self.callman.add_db_signal("event-add", self.redraw)
        self.callman.add_db_signal("event-delete", self.redraw)
#        self.callman.add_db_signal("event-rebuild", self.redraw)
        self.callman.add_db_signal("citation-update", self.redraw)
        self.callman.add_db_signal("citation-add", self.redraw)
        self.callman.add_db_signal("citation-delete", self.redraw)
#        self.callman.add_db_signal("citation-rebuild", self.redraw)
        self.callman.add_db_signal("person-update", self.person_update)
        self.callman.add_db_signal("person-add", self.person_update)
        self.callman.add_db_signal("person-delete", self.redraw)
#        self.callman.add_db_signal("person-rebuild", self.person_rebuild)
        self.callman.add_db_signal("family-update", self.family_update)
        self.callman.add_db_signal("family-add", self.family_add)
        self.callman.add_db_signal("family-delete", self.family_delete)
#        self.callman.add_db_signal("family-rebuild", self.family_rebuild)
        self.callman.add_db_signal("tag-update", self.redraw)
        self.callman.add_db_signal("tag-add", self.redraw)
        self.callman.add_db_signal("tag-delete", self.redraw)
#        self.callman.add_db_signal("tag-rebuild", self.redraw)
        self.callman.add_db_signal("note-update", self.redraw)
        self.callman.add_db_signal("note-add", self.redraw)
        self.callman.add_db_signal("note-delete", self.redraw)
#        self.callman.add_db_signal("note-rebuild", self.redraw)

    def font_changed(self):
        """
        Handle font change.
        """
        self.reload_symbols()
        self.build_tree()

    def navigation_type(self):
        """
        Object type of the view.
        """
        return "Person"

    def can_configure(self):
        """
        See :class:`~gui.views.pageview.PageView
        :return: bool
        """
        return True

    def goto_handle(self, handle):
        """
        Change to new person.
        """
        self.change_person(handle)

    def config_update(self, client, cnxn_id, entry, data):
        """
        Handle configuration option change.
        """
        self.redraw()

    def build_tree(self):
        """
        Build the view.
        """
        self.redraw()

    def person_update(self, handle_list):
        """
        Handle update if person changed.
        """
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def person_rebuild(self):
        """
        Large change to person database
        """
        if self.active:
            self.bookmarks.redraw()
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_update(self, handle_list):
        """
        Handle family update.
        """
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_add(self, handle_list):
        """
        Handle addition of family.
        """
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_delete(self, handle_list):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def family_rebuild(self):
        if self.active:
            person = self.get_active()
            if person:
                while not self.change_person(person):
                    pass
            else:
                self.change_person(None)
        else:
            self.dirty = True

    def change_page(self):
        NavigationView.change_page(self)
        self.uistate.clear_filter_results()

    def get_stock(self):
        """
        Return the name of the stock icon to use for the display.
        This assumes that this icon has already been registered with
        GNOME as a stock icon.
        """
        return "gramps-person"

    def get_viewtype_stock(self):
        """Type of view in category"""
        return "gramps-person"

    def build_widget(self):
        """
        Build the widget that contains the view, see
        :class:`~gui.views.pageview.PageView
        """
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.set_border_width(6)
        self.header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.child = None
        self.scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.viewport = Gtk.Viewport()
        self.viewport.add(self.vbox)
        self.scroll.add(self.viewport)
        container.pack_start(self.header, False, False, 0)
        container.pack_end(self.scroll, True, True, 0)
        return container

    additional_ui = [  # Defines the UI string for UIManager
        """
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">"""
        """Organize Bookmarks...</attribute>
        </item>
      </section>
      <section>
        <item>
          <attribute name="action">win.HomePerson</attribute>
          <attribute name="label" translatable="yes">_Home</attribute>
        </item>
      </section>
      </placeholder>
""",
        """
      <placeholder id='otheredit'>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label" translatable="yes">Edit...</attribute>
        </item>
        <item>
          <attribute name="action">win.AddParents</attribute>
          <attribute name="label" translatable="yes">"""
        """Add New Parents...</attribute>
        </item>
        <item>
          <attribute name="action">win.ShareFamily</attribute>
          <attribute name="label" translatable="yes">"""
        """Add Existing Parents...</attribute>
        </item>
        <item>
          <attribute name="action">win.AddSpouse</attribute>
          <attribute name="label" translatable="yes">Add Partner...</attribute>
        </item>
        <item>
          <attribute name="action">win.ChangeOrder</attribute>
          <attribute name="label" translatable="yes">_Reorder</attribute>
        </item>
        <item>
          <attribute name="action">win.FilterEdit</attribute>
          <attribute name="label" translatable="yes">"""
        """Person Filter Editor</attribute>
        </item>
      </placeholder>
""",
        """
      <section id="AddEditBook">
        <item>
          <attribute name="action">win.AddBook</attribute>
          <attribute name="label" translatable="yes">_Add Bookmark</attribute>
        </item>
        <item>
          <attribute name="action">win.EditBook</attribute>
          <attribute name="label" translatable="no">%s...</attribute>
        </item>
      </section>
"""
        % _("Organize Bookmarks"),  # Following are the Toolbar items
        """
    <placeholder id='CommonNavigation'>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-previous</property>
        <property name="action-name">win.Back</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the previous object in the history</property>
        <property name="label" translatable="yes">_Back</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-next</property>
        <property name="action-name">win.Forward</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the next object in the history</property>
        <property name="label" translatable="yes">_Forward</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RO'>
      <object class="GtkToolButton">
        <property name="icon-name">go-home</property>
        <property name="action-name">win.HomePerson</property>
        <property name="tooltip_text" translatable="yes">"""
        """Go to the default person</property>
        <property name="label" translatable="yes">_Home</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
""",
        """
    <placeholder id='BarCommonEdit'>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text" translatable="yes">"""
        """Edit the active person</property>
        <property name="label" translatable="yes">Edit...</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-add</property>
        <property name="action-name">win.AddParents</property>
        <property name="tooltip_text" translatable="yes">"""
        """Add a new set of parents</property>
        <property name="label" translatable="yes">Add</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-parents-open</property>
        <property name="action-name">win.ShareFamily</property>
        <property name="tooltip_text" translatable="yes">"""
        """Add person as child to an existing family</property>
        <property name="label" translatable="yes">Share</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gramps-spouse</property>
        <property name="action-name">win.AddSpouse</property>
        <property name="tooltip_text" translatable="yes">"""
        """Add a new family with person as parent</property>
        <property name="label" translatable="yes">Partner</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">view-sort-ascending</property>
        <property name="action-name">win.ChangeOrder</property>
        <property name="tooltip_text" translatable="yes">"""
        """Change order of parents and families</property>
        <property name="label" translatable="yes">_Reorder</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
     """,
    ]

    def define_actions(self):
        NavigationView.define_actions(self)

        self.order_action = ActionGroup(name=self.title + "/ChangeOrder")
        self.order_action.add_actions([("ChangeOrder", self.reorder)])

        self.family_action = ActionGroup(name=self.title + "/Family")
        self.family_action.add_actions(
            [
                ("Edit", self.edit_active, "<PRIMARY>Return"),
                ("AddSpouse", self.add_spouse),
                ("AddParents", self.add_parents),
                ("ShareFamily", self.select_parents),
            ]
        )

        self._add_action("FilterEdit", callback=self.filter_editor)
        self._add_action("PRIMARY-J", self.jump, "<PRIMARY>J")

        self._add_action_group(self.order_action)
        self._add_action_group(self.family_action)

        self.uimanager.set_actions_sensitive(self.order_action, self.reorder_sensitive)
        self.uimanager.set_actions_sensitive(self.family_action, False)

    def filter_editor(self, *obj):
        try:
            FilterEditor("Person", CUSTOM_FILTERS, self.dbstate, self.uistate)
        except WindowActiveError:
            return

    def change_db(self, db):
        # reset the connects
        self._change_db(db)
        if self.child:
            list(map(self.vbox.remove, self.vbox.get_children()))
            list(map(self.header.remove, self.header.get_children()))
            self.child = None
        if self.active:
            self.bookmarks.redraw()
        self.redraw()

    def redraw(self, *obj):
        active_person = self.get_active()
        if active_person:
            self.change_person(active_person)
        else:
            self.change_person(None)

    def change_person(self, obj):
        self.change_active(obj)
        try:
            return self._change_person(obj)
        except AttributeError as msg:
            import traceback

            exc = traceback.format_exc()
            _LOG.error(str(msg) + "\n" + exc)
            from gramps.gui.dialog import RunDatabaseRepair

            RunDatabaseRepair(str(msg), parent=self.uistate.window)
            self.redrawing = False
            return True

    def _change_person(self, obj):
        if self.redrawing:
            return False
        self.redrawing = True

        list(map(self.header.remove, self.header.get_children()))
        list(map(self.vbox.remove, self.vbox.get_children()))

        person = None
        if obj:
            person = self.dbstate.db.get_person_from_handle(obj)
        if not person:
            self.uimanager.set_actions_sensitive(self.family_action, False)
            self.uimanager.set_actions_sensitive(self.order_action, False)
            self.redrawing = False
            return
        self.uimanager.set_actions_sensitive(self.family_action, True)

        home = self.dbstate.db.get_default_person()
        self.active_profile = PersonGrampsFrame(
            self.dbstate,
            self.uistate,
            person,
            "active",
            "preferences.profile.person",
            self._config,
            self.callback_router,
            relation=home,
            defaults=self.CONFIGSETTINGS
        )

        body = Gtk.HBox(expand=True, spacing=3)
        parents_box = Gtk.VBox(spacing=3)
        parents = get_parent_profiles(
            self.dbstate,
            self.uistate,
            person,
            router=self.callback_router,
            config=self._config,
            defaults=self.CONFIGSETTINGS
        )
        if parents is not None:
            parents_box.pack_start(parents, expand=False, fill=False, padding=0)

        spouses_box = Gtk.VBox(spacing=3)
        spouses = get_spouse_profiles(
            self.dbstate,
            self.uistate,
            person,
            router=self.callback_router,
            config=self._config,
            defaults=self.CONFIGSETTINGS
        )
        if spouses is not None:
            spouses_box.pack_start(spouses, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.show-timeline"):
            timeline_box = Gtk.VBox(spacing=3)
            timeline = get_timeline_profiles(
                self.dbstate,
                self.uistate,
                person,
                router=self.callback_router,
                config=self._config,
            )
            if timeline is not None:
                timeline_box.pack_start(timeline, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.show-citations"):
            citations_box = Gtk.VBox(spacing=3)
            citations = get_citation_profiles(
                self.dbstate,
                self.uistate,
                person,
                self.callback_router,
                "preferences.profile.person",
                self._config,
            )
            if citations is not None:
                citations_box.pack_start(citations, expand=False, fill=False, padding=0)

        if self._config.get("preferences.profile.person.layout.families-stacked"):
            families_box = Gtk.VBox(spacing=3)
            families_box.pack_start(parents_box, expand=False, fill=False, padding=0)
            families_box.pack_start(spouses_box, expand=False, fill=False, padding=0)
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(families_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-timeline"):
                body.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-citations"):
                body.pack_start(citations_box, expand=True, fill=True, padding=0)
            if not self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(families_box, expand=True, fill=True, padding=0)
        else:
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(spouses_box, expand=True, fill=True, padding=0)
            else:
                body.pack_start(parents_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-timeline"):
                body.pack_start(timeline_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.show-citations"):
                body.pack_start(citations_box, expand=True, fill=True, padding=0)
            if self._config.get("preferences.profile.person.layout.spouses-left"):
                body.pack_start(parents_box, expand=True, fill=True, padding=0)
            else:
                body.pack_start(spouses_box, expand=True, fill=True, padding=0)

        if self._config.get("preferences.profile.person.layout.pinned-header"):
            self.header.pack_start(self.active_profile, False, False, 0)
            self.header.show_all()
        else:
            self.vbox.pack_start(self.active_profile, False, False, 0)
        self.child = body
        self.vbox.pack_start(self.child, True, True, 0)
        self.vbox.show_all()

        family_handle_list = person.get_parent_family_handle_list()
        self.reorder_sensitive = len(family_handle_list) > 1
        family_handle_list = person.get_family_handle_list()
        if not self.reorder_sensitive:
            self.reorder_sensitive = len(family_handle_list) > 1

        self.redrawing = False
        self.uistate.modify_statusbar(self.dbstate)
        self.uimanager.set_actions_sensitive(self.order_action, self.reorder_sensitive)
        self.dirty = False
        return True

    def callback_router(self, obj, event, handle, action, data=None):
        if action == "link-person":
            self.change_person(handle)            
        if action == "copy-clipboard":
            self.copy_to_clipboard(data, [handle])

    def marriage_symbol(self, family, markup=True):
        if family:
            father = mother = None
            hdl1 = family.get_father_handle()
            if hdl1:
                father = self.dbstate.db.get_person_from_handle(hdl1).gender
            hdl2 = family.get_mother_handle()
            if hdl2:
                mother = self.dbstate.db.get_person_from_handle(hdl2).gender
            if father != mother:
                symbol = self.marr
            elif father == Person.MALE:
                symbol = self.homom
            else:
                symbol = self.homof
            if markup:
                msg = '<span size="12000" >%s</span>' % symbol
            else:
                msg = symbol
        else:
            msg = ""
        return msg

    def change_to(self, obj, handle):
        self.change_active(handle)

    def reorder_button_press(self, obj, event, handle):
        if button_activated(event, _LEFT_BUTTON):
            self.reorder(obj)

    def reorder(self, *obj):
        if self.get_active():
            try:
                Reorder(self.dbstate, self.uistate, [], self.get_active())
            except WindowActiveError:
                pass

    def config_connect(self):
        """
        Overwriten from  :class:`~gui.views.pageview.PageView method
        This method will be called after the ini file is initialized,
        use it to monitor changes in the ini file
        """
        for item in self.CONFIGSETTINGS:
            self._config.connect(item[0], self.config_update)

    def create_grid(self):
        """
        Gtk.Grid for config panels (tabs).
        """
        grid = Gtk.Grid(row_spacing=6, column_spacing=6, column_homogeneous=False)
        grid.set_border_width(12)
        return grid

    def _config_facts_fields(self, configdialog, grid, space, start_row, start_col=1, number=8, extra=False):
        """
        Build facts field configuration section.
        """
        count = 1
        row = start_row
        text = _("Facts field")
        key = "facts-field"
        if extra:
            text = _("Extra field")
            key = "extra-field"
        while row < start_row + number:
            option = "{}.{}-{}".format(space, key, count)
            user_select = FrameFieldSelector(
                option, self._config, self.dbstate, self.uistate, count,
                dbid=True, defaults=self.CONFIGSETTINGS, text=text
            )
            grid.attach(user_select, start_col, row, 2, 1)
            count = count + 1
            row = row + 1
        option = "{}.{}-skip-birth-alternates".format(space, key)
        configdialog.add_checkbox(
            grid, _("Skip birth alternatives if birth found"),
            row, option, start=start_col,
            tooltip=_("If enabled then if a birth event was found other events considered to be birth alternatives such as baptism or christening will not be displayed.")
        )
        row = row + 1
        option = "{}.{}-skip-death-alternates".format(space, key)
        configdialog.add_checkbox(
            grid, _("Skip death alternates if death found"),
            row, option, start=start_col,
            tooltip=_("If enabled then if a death event was found other events considered to be death alternatives such as burial or cremation will not be displayed.")
        )
        row = row + 1

    def _config_metadata_attributes(self, grid, space, start_row, start_col=1, number=8):
        """
        Build metadata custom attribute configuration section.
        """
        count = 1
        row = start_row
        while row < start_row + number:
            option = "{}.metadata-attribute-{}".format(space, count)
            attr_select = AttributeSelector(
                option, self._config, self.dbstate.db, "Person", dbid=True,
                tooltip=_("This option allows you to select the name of a custom user defined attribute about the person. The value of the attribute, if one is found, will then be displayed in the metadata section of the user frame beneath the Gramps Id.")
            )
            label = Gtk.Label(
                halign=Gtk.Align.START, label="{} {}: ".format(_("Metadata attribute"), count)
            )
            grid.attach(label, start_col, row, 1, 1)
            grid.attach(attr_select, start_col + 1, row, 1, 1)
            count = count + 1
            row = row + 1

    def layout_panel(self, configdialog):
        """
        Builds layout and styling options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Layout Options"), 0, bold=True)
        configdialog.add_checkbox(
            grid, _("Pin active person header so it does not scroll"),
            1, "preferences.profile.person.layout.pinned-header",
            tooltip=_("Enabling this option pins the header frame so it will not scroll with the rest of the view.")
        )
        configdialog.add_checkbox(
            grid, _("Place spouses & children on left side"),
            2, "preferences.profile.person.layout.spouses-left",
        )
        configdialog.add_checkbox(
            grid, _("Stack parents & spouses in a single column"),
            3, "preferences.profile.person.layout.families-stacked",
        )
        configdialog.add_checkbox(
            grid, _("Show event timeline"),
            4, "preferences.profile.person.layout.show-timeline",
        )
        configdialog.add_checkbox(
            grid, _("Show associated citations"),
            5, "preferences.profile.person.layout.show-citations",
        )
        configdialog.add_text(grid, _("Styling Options"), 6, bold=True)
        configdialog.add_checkbox(
            grid, _("Use smaller font for detail attributes"),
            7, "preferences.profile.person.layout.use-smaller-detail-font",
            tooltip=_("Enabling this option uses a smaller font for all the detailed information than used for the title.")
        )
        configdialog.add_spinner(
            grid, _("Desired border width"),
            8, "preferences.profile.person.layout.border-width",
            (0, 5),
        )
        configdialog.add_checkbox(
            grid, _("Enable coloring schemes"),
            9, "preferences.profile.person.layout.use-color-scheme",
            tooltip=_("Enabling this option enables coloring schemes for the rendered frames. People and families currently use the default Gramps color scheme defined in the global preferences. This view also supports other user customizable color schemes to choose from for some of the object groups such as the timeline.")
        )
        configdialog.add_checkbox(
            grid, _("Right to left"),
            10, "preferences.profile.person.layout.right-to-left",
            tooltip=_("TBD TODO. If implemented this would modify the frame layout and right justify text fields which might provide a nicer view for those who read right to left like Hebrew, Arabic and Persian.")
        )
        configdialog.add_checkbox(
            grid, _("Sort tags by name not priority"),
            11, "preferences.profile.person.layout.sort-tags-by-name",
            tooltip=_("Enabling this option will sort tags by name before displaying them. By default they sort by the priority in which they are organized in the tag organization tool.")
        )
        configdialog.add_checkbox(
            grid, _("Enable warnings"),
            12, "preferences.profile.person.layout.enable-warnings",
            tooltip=_("Enabling this will raise a warning dialog asking for confirmation before performing an action that removes or deletes data as a safeguard.")
        )
        configdialog.add_checkbox(
            grid, _("Enable tooltips"),
            13, "preferences.profile.person.layout.enable-tooltips",
            tooltip=_("TBD TODO. If implemented some tooltips may be added to the view as an aid for new Gramps users which would quickly become annoying so this would turn them off for experienced users.")
        )
        return _("Layout"), grid

    def active_panel(self, configdialog):
        """
        Builds active person options section for the configuration dialog
        """
        grid = self.create_grid()        
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.person.active.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            2, "preferences.profile.person.active.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            3, "preferences.profile.person.active.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            4, "preferences.profile.person.active.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_text(grid, _("Display Attributes"), 5, bold=True)
        configdialog.add_checkbox(
            grid, _("Show gender"),
            6, "preferences.profile.person.active.show-gender"
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            7, "preferences.profile.person.active.show-age",
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 8, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.active", 9)
        configdialog.add_text(grid, _("Extra Fact Display Fields"), 8, start=3, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.active", 9, start_col=3, extra=True)
        configdialog.add_text(grid, _("Metadata Display Custom Attributes"), 8, start=5, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.active", 9, start_col=5)
        return _("Person"), grid

    def parents_panel(self, configdialog):
        """
        Builds parents options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.person.parent.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            2, "preferences.profile.person.parent.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            3, "preferences.profile.person.parent.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            4, "preferences.profile.person.parent.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Matrilineal mode (inverts couple)"),
            5, "preferences.profile.person.parent.show-matrilineal",
            tooltip=_("Enabling this option will switch the placement of the male and female roles in the couple relationship.")
        )
        configdialog.add_checkbox(
            grid, _("Expand children by default"),
            6, "preferences.profile.person.parent.expand-children",
            tooltip=_("Enabling this option will automatically expand the list of children when the page is rendered.")
        )
        configdialog.add_text(grid, _("Display Attributes"), 7, bold=True)
        configdialog.add_checkbox(
            grid, _("Show gender"),
            8, "preferences.profile.person.parent.show-gender"
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            9, "preferences.profile.person.parent.show-age",
        )
        configdialog.add_checkbox(
            grid, _("Show divorce or divorce equivalent"),
            10, "preferences.profile.person.parent.show-divorce",
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.parent", 12)
        configdialog.add_text(grid, _("Metadata Display Custom Attributes"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.parent", 12, start_col=3)
        return _("Parents"), grid

    def spouses_panel(self, configdialog):
        """
        Builds spouses options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.person.spouse.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            2, "preferences.profile.person.spouse.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            3, "preferences.profile.person.spouse.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            4, "preferences.profile.person.spouse.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Show spouse only"),
            7, "preferences.profile.person.spouse.show-spouse-only",
        )
        configdialog.add_checkbox(
            grid, _("Expand children by default"),
            8, "preferences.profile.person.spouse.expand-children",
            tooltip=_("Enabling this option will automatically expand the list of children when the page is rendered.")
        )
        configdialog.add_text(grid, _("Display Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show gender"),
            10, "preferences.profile.person.spouse.show-gender"
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            11, "preferences.profile.person.spouse.show-age",
        )
        configdialog.add_checkbox(
            grid, _("Show divorce or divorce equivalent"),
            12, "preferences.profile.person.spouse.show-divorce",
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 13, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.spouse", 14)
        configdialog.add_text(grid, _("Metadata Display Custom Attributes"), 13, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.spouse", 14, start_col=3)
        return _("Spouses"), grid

    def children_panel(self, configdialog):
        """
        Builds children options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.person.child.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            2, "preferences.profile.person.child.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            3, "preferences.profile.person.child.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            4, "preferences.profile.person.child.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Number children"),
            7, "preferences.profile.person.child.number-children",
        )
        configdialog.add_text(grid, _("Display Attributes"), 8, bold=True)
        configdialog.add_checkbox(
            grid, _("Show gender"),
            9, "preferences.profile.person.child.show-gender"
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            10, "preferences.profile.person.child.show-age",
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.child", 12)
        configdialog.add_text(grid, _("Metadata Display Custom Attributes"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.child", 12, start_col=3)
        return _("Children"), grid

    def siblings_panel(self, configdialog):
        """
        Builds siblings options section for the configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Event display format"),
            1, "preferences.profile.person.sibling.event-format",
            EVENT_DISPLAY_MODES,
        )
        configdialog.add_combo(
            grid, _("Tag display mode"),
            2, "preferences.profile.person.sibling.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            3, "preferences.profile.person.sibling.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            4, "preferences.profile.person.sibling.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Number children"),
            7, "preferences.profile.person.sibling.number-children",
        )
        configdialog.add_text(grid, _("Display Attributes"), 8, bold=True)
        configdialog.add_checkbox(
            grid, _("Show gender"),
            9, "preferences.profile.person.sibling.show-gender"
        )
        configdialog.add_checkbox(
            grid, _("Show age at death and if selected burial"),
            10, "preferences.profile.person.sibling.show-age",
        )
        configdialog.add_text(grid, _("Fact Display Fields"), 11, bold=True)
        self._config_facts_fields(configdialog, grid, "preferences.profile.person.sibling", 12)
        configdialog.add_text(grid, _("Metadata Display Custom Attributes"), 11, start=3, bold=True)
        self._config_metadata_attributes(grid, "preferences.profile.person.sibling", 12, start_col=3)
        return _("Siblings"), grid

    def timeline_panel(self, configdialog):
        """
        Builds active person timeline options section for the configuration dialog
        """
        grid1 = self.create_grid()
        configdialog.add_text(grid1, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid1, _("Timeline color scheme"),
            1, "preferences.profile.person.timeline.color-scheme",
            TIMELINE_COLOR_MODES,
        )
        configdialog.add_combo(
            grid1, _("Tag display mode"),
            2, "preferences.profile.person.timeline.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid1, _("Maximum tags per line"),
            3, "preferences.profile.person.timeline.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid1, _("Image display mode"),
            4, "preferences.profile.person.timeline.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid1, _("Show year and age"),
            5, "preferences.profile.person.timeline.show-age",
            tooltip=_("Enabling this option will show the year of the event and the age of the active person at that time if it can be calculated.")
        )
        configdialog.add_text(grid1, _("Display Attributes"), 6, bold=True)
        configdialog.add_checkbox(
            grid1, _("Show role always not just secondary events"),
            7, "preferences.profile.person.timeline.show-role-always",
            tooltip=_("Enabling this option will always show the role of the active person in the event. This is normally implicit if they had none or they were the primary participant. Note their role is always displayed for secondary events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show description"),
            8, "preferences.profile.person.timeline.show-description",
            tooltip=_("Enabling this option will show the event description if one is available.")
        )
        configdialog.add_checkbox(
            grid1, _("Show registered participants if more than one person"),
            9, "preferences.profile.person.timeline.show-participants",
            tooltip=_("Enabling this option will show the other participants in shared events.")
        )
        configdialog.add_checkbox(
            grid1, _("Show source count"),
            10, "preferences.profile.person.timeline.show-source-count",
            tooltip=_("Enabling this option will include a count of the number of unique sources cited from in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show citation count"),
            11, "preferences.profile.person.timeline.show-citation-count",
            tooltip=_("Enabling this option will include a count of the number of citations in support of the information about the event.")
        )
        configdialog.add_checkbox(
            grid1, _("Show best confidence rating"),
            12, "preferences.profile.person.timeline.show-best-confidence",
            tooltip=_("Enabling this option will show the highest user defined confidence rating found among all the citations in support of the information about the event.")
        )
        grid2 = self.create_grid()
        configdialog.add_text(grid2, _("Category Filters"), 0, bold=True)
        configdialog.add_checkbox(
            grid2, _("Show vital"),
            1, "preferences.profile.person.timeline.show-class-vital",
            tooltip=_("Enabling this option will show all vital events for the person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others.")
        )
        configdialog.add_checkbox(
            grid2, _("Show family"),
            2, "preferences.profile.person.timeline.show-class-family",
            tooltip=_("Enabling this option will show all family related events for the active person on the timeline. The list of family events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show religious"),
            3, "preferences.profile.person.timeline.show-class-religious",
            tooltip=_("Enabling this option will show all religious events for the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show vocational"),
            4, "preferences.profile.person.timeline.show-class-vocational",
            tooltip=_("Enabling this option will show all vocational events for the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show academic"),
            5, "preferences.profile.person.timeline.show-class-academic",
            tooltip=_("Enabling this option will show all academic events for the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show travel"),
            6, "preferences.profile.person.timeline.show-class-travel",
            tooltip=_("Enabling this option will show all travel events for the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show legal"),
            7, "preferences.profile.person.timeline.show-class-legal",
            tooltip=_("Enabling this option will show all legal events for the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show residence"),
            8, "preferences.profile.person.timeline.show-class-residence",
            tooltip=_("Enabling this option will show all residence events for the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show other"),
            9, "preferences.profile.person.timeline.show-class-other",
            tooltip=_("Enabling this option will show all other events for the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid2, _("Show custom"),
            10, "preferences.profile.person.timeline.show-class-custom",
            tooltip=_("Enabling this option will show all user defined custom events for the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor.")
        )
        grid3 = self.create_grid()
        configdialog.add_text(grid3, _("Relationship Filters"), 0, bold=True)
        configdialog.add_spinner(
            grid3, _("Generations of ancestors to examine"),
            1, "preferences.profile.person.timeline.generations-ancestors",
            (1, 3),
        )
        configdialog.add_spinner(
            grid3, _("Generations of offspring to examine"),
            2, "preferences.profile.person.timeline.generations-offspring",
            (1, 3),
        )
        configdialog.add_checkbox(
            grid3, _("Include events for father and grandfathers"),
            3, "preferences.profile.person.timeline.show-family-father",
            tooltip=_("Enabling this option will include events for fathers, stepfathers, and grandfathers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for mother and grandmothers"),
            4, "preferences.profile.person.timeline.show-family-mother",
            tooltip=_("Enabling this option will include events for mothers, stepmothers, and grandmothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for brothers and stepbrothers"),
            5, "preferences.profile.person.timeline.show-family-brother",
            tooltip=_("Enabling this option will include events for brothers and stepbrothers of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for sisters and stepsisters"),
            6, "preferences.profile.person.timeline.show-family-sister",
            tooltip=_("Enabling this option will include events for sisters and stepsisters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for wives"),
            7, "preferences.profile.person.timeline.show-family-wife",
            tooltip=_("Enabling this option will include events for the wives of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for husbands"),
            8, "preferences.profile.person.timeline.show-family-husband",
            tooltip=_("Enabling this option will include events for the husbands of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for sons and grandsons"),
            9, "preferences.profile.person.timeline.show-family-son",
            tooltip=_("Enabling this option will include events for the sons and grandsons of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        configdialog.add_checkbox(
            grid3, _("Include events for daughters and granddaughters"),
            10, "preferences.profile.person.timeline.show-family-daughter",
            tooltip=_("Enabling this option will include events for the daughters and granddaughters of the active person in the timeline if they occurred during the life of the active person. Note if no relationship category filters are enabled that the birth and death events of these relations are always evaluated for inclusion.")
        )
        grid4 = self.create_grid()
        configdialog.add_text(grid4, _("Relationship Category Filters"), 0, bold=True)
        configdialog.add_checkbox(
            grid4, _("Show vital"),
            1, "preferences.profile.person.timeline.show-family-class-vital",
            tooltip=_("Enabling this option will show all vital events for the eligible relations of the active person on the timeline. In the event editor these are identfied as birth, baptism, death, burial, cremation and adopted. Note if this is disabled that birth and death events or their equivalents will always included regardless, so disabling it only filters out the others.")
        )
        configdialog.add_checkbox(
            grid4, _("Show family"),
            2, "preferences.profile.person.timeline.show-family-class-family",
            tooltip=_("Enabling this option will show all family related events for the eligible relations of the active person on the timeline. The list of family events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show religious"),
            3, "preferences.profile.person.timeline.show-family-class-religious",
            tooltip=_("Enabling this option will show all religious related events for the eligible relations of the active person on the timeline. The list of religious events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show vocational"),
            4, "preferences.profile.person.timeline.show-family-class-vocational",
            tooltip=_("Enabling this option will show all vocational related events for the eligible relations of the active person on the timeline. The list of vocational events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show academic"),
            5, "preferences.profile.person.timeline.show-family-class-academic",
            tooltip=_("Enabling this option will show all academic related events for the eligible relations of the active person on the timeline. The list of academic events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show travel"),
            6, "preferences.profile.person.timeline.show-family-class-travel",
            tooltip=_("Enabling this option will show all travel related events for the eligible relations of the active person on the timeline. The list of travel events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show legal"),
            7, "preferences.profile.person.timeline.show-family-class-legal",
            tooltip=_("Enabling this option will show all legal related events for the eligible relations of the active person on the timeline. The list of legal events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show residence"),
            8, "preferences.profile.person.timeline.show-family-class-residence",
            tooltip=_("Enabling this option will show all residence related events for the eligible relations of the active person on the timeline. The list of residence events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show other"),
            9, "preferences.profile.person.timeline.show-family-class-other",
            tooltip=_("Enabling this option will show all other events for the eligible relations of the active person on the timeline except custom user defined ones. The list of other events is the same as in the event type selector in the event editor.")
        )
        configdialog.add_checkbox(
            grid4, _("Show custom"),
            10, "preferences.profile.person.timeline.show-family-class-custom",
            tooltip=_("Enabling this option will show all user defined custom events for the eligible relations of the active person on the timeline. The list of custom events is the same as in the event type selector in the event editor.")
        )
        grid = Gtk.Grid()
        grid.attach(grid1, 0, 0, 1, 1)
        grid.attach(grid2, 1, 0, 1, 1)
        grid.attach(grid3, 2, 0, 1, 1)
        grid.attach(grid4, 3, 0, 1, 1)
        return _("Timeline"), grid

    def citations_panel(self, configdialog):
        """
        Builds citations options section for configuration dialog
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("Display Options"), 0, bold=True)
        configdialog.add_combo(
            grid, _("Tag display mode"),
            1, "preferences.profile.person.citation.tag-format",
            TAG_DISPLAY_MODES,
        )
        configdialog.add_spinner(
            grid, _("Maximum tags per line"),
            2, "preferences.profile.person.citation.tag-width",
            (1, 20),
        )
        configdialog.add_combo(
            grid, _("Image display mode"),
            3, "preferences.profile.person.citation.image-mode",
            IMAGE_DISPLAY_MODES,
        )
        configdialog.add_checkbox(
            grid, _("Sort citations by date"),
            4, "preferences.profile.person.citation.sort-by-date",
            tooltip=_("Enabling this option will sort the citations by date.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations about the person"),
            5, "preferences.profile.person.citation.include-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes like names and person associations in addition to the ones directly on the person themselves.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a child"),
            6, "preferences.profile.person.citation.include-parent-family",
            tooltip=_("Enabling this option will include citations related to the membership of the person as a child in other families.")
        )
        configdialog.add_checkbox(
            grid, _("Include citations related to the persons family membership as a head of household"),
            7, "preferences.profile.person.citation.include-family",
            tooltip=_("Enabling this option will include citations on the families this person formed with other partners.")
        )
        configdialog.add_checkbox(
            grid, _("Include indirect citations related to the persons family membership as a head of household"),
            8, "preferences.profile.person.citation.include-family-indirect",
            tooltip=_("Enabling this option will include citations on nested attributes about the families this person formed with other partners.")
        )
        configdialog.add_text(grid, _("Attributes"), 9, bold=True)
        configdialog.add_checkbox(
            grid, _("Show date"),
            10, "preferences.profile.person.citation.show-date",
            tooltip=_("Enabling this option will show the citation date if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show publisher"),
            11, "preferences.profile.person.citation.show-publisher",
            tooltip=_("Enabling this option will show the publisher information if it is available.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference type"),
            12, "preferences.profile.person.citation.show-reference-type",
            tooltip=_("Enabling this option will display what type of citation it is. Direct is one related to the person or a family they formed, indirect would be related to some nested attribute like a name or person association.")
        )
        configdialog.add_checkbox(
            grid, _("Show reference description"),
            13, "preferences.profile.person.citation.show-reference-description",
            tooltip=_("Enabling this option will display a description of the type of data the citation supports. For direct citations this would be person or family, indirect ones could be primary name, an attribute, association, address, and so forth.")
        )
        configdialog.add_checkbox(
            grid, _("Show confidence rating"),
            14, "preferences.profile.person.citation.show-confidence",
            tooltip=_("Enabling this option will display the user selected confidence level for the citation.")
        )
        return _("Citations"), grid

    def color_panel(self, configdialog):
        """
        Add the tab to set defaults colors for graph boxes.
        """
        grid = self.create_grid()
        configdialog.add_text(grid, _("See global preferences for option to switch between light and dark color schemes"), 0, bold=True)
        configdialog.add_text(grid, _("The default Gramps person color scheme is also managed under global preferences"), 1, bold=True)

        color_type = {'Confidence': _('Confidence color scheme'),
                      'Relation': _('Relationship color scheme'),
                      'Event': _('Event category color scheme')}

        # for confidence scheme
        bg_very_high_text = _('Background for Very High')
        bg_high_text = _('Background for High')
        bg_normal_text = _('Background for Normal')
        bg_low_text = _('Background for Low')
        bg_very_low_text = _('Background for Very Low')
        brd_very_high_text = _('Border for Very High')
        brd_high_text = _('Border for High')
        brd_normal_text = _('Border for Normal')
        brd_low_text = _('Border for Low')
        brd_very_low_text = _('Border for Very Low')

        # for relation scheme
        bg_active = _('Background for Active Person')
        bg_spouse = _('Background for Spouse')
        bg_father = _('Background for Father')
        bg_mother = _('Background for Mother')
        bg_brother = _('Background for Brother')
        bg_sister = _('Background for Sister')
        bg_son = _('Background for Son')
        bg_daughter = _('Background for Daughter')
        bg_none = _('Background for None')
        brd_active = _('Border for Active Person')
        brd_spouse = _('Border for Spouse')
        brd_father = _('Border for Father')
        brd_mother = _('Border for Mother')
        brd_brother = _('Border for Brother')
        brd_sister = _('Border for Sister')
        brd_son = _('Border for Son')
        brd_daughter = _('Border for Daughter')
        brd_none = _('Border for None')

        # for event category scheme
        bg_vital = _('Background for Vital Events')
        bg_family = _('Background for Family Events')
        bg_religious = _('Background for Religious Events')
        bg_vocational = _('Background for Vocational Events')
        bg_academic = _('Background for Academic Events')
        bg_travel = _('Background for Travel Events')
        bg_legal = _('Background for Legal Events')
        bg_residence = _('Background for Residence Events')
        bg_other = _('Background for Other Events')
        bg_custom = _('Background for Custom Events')
        brd_vital = _('Border for Vital Events')
        brd_family = _('Border for Family Events')
        brd_religious = _('Border for Religious Events')
        brd_vocational = _('Border for Vocational Events')
        brd_academic = _('Border for Academic Events')
        brd_travel = _('Border for Travel Events')
        brd_legal = _('Border for Legal Events')
        brd_residence = _('Border for Residence Events')
        brd_other = _('Border for Other Events')
        brd_custom = _('Border for Custom Events')
        
        # color label, config constant, group grid row, column, color type
        color_list = [
            # for confidence scheme
            (bg_very_high_text, 'preferences.profile.colors.confidence.very-high', 1, 1, 'Confidence'),
            (bg_high_text, 'preferences.profile.colors.confidence.high', 2, 1, 'Confidence'),
            (bg_normal_text, 'preferences.profile.colors.confidence.normal', 3, 1, 'Confidence'),
            (bg_low_text, 'preferences.profile.colors.confidence.low', 4, 1, 'Confidence'),
            (bg_very_low_text, 'preferences.profile.colors.confidence.very-low', 5, 1, 'Confidence'),
            (brd_very_high_text, 'preferences.profile.colors.confidence.border-very-high', 1, 4, 'Confidence'),
            (brd_high_text, 'preferences.profile.colors.confidence.border-high', 2, 4, 'Confidence'),
            (brd_normal_text, 'preferences.profile.colors.confidence.border-normal', 3, 4, 'Confidence'),
            (brd_low_text, 'preferences.profile.colors.confidence.border-low', 4, 4, 'Confidence'),
            (brd_very_low_text, 'preferences.profile.colors.confidence.border-very-low', 5, 4, 'Confidence'),

            # for relation scheme
            (bg_active, 'preferences.profile.colors.relations.active', 1, 1, 'Relation'),
            (bg_spouse, 'preferences.profile.colors.relations.spouse', 2, 1, 'Relation'),
            (bg_father, 'preferences.profile.colors.relations.father', 3, 1, 'Relation'),
            (bg_mother, 'preferences.profile.colors.relations.mother', 4, 1, 'Relation'),
            (bg_brother, 'preferences.profile.colors.relations.brother', 5, 1, 'Relation'),
            (bg_sister, 'preferences.profile.colors.relations.sister', 6, 1, 'Relation'),
            (bg_son, 'preferences.profile.colors.relations.son', 7, 1, 'Relation'),
            (bg_daughter, 'preferences.profile.colors.relations.daughter', 8, 1, 'Relation'),
            (bg_none, 'preferences.profile.colors.relations.none', 9, 1, 'Relation'),
            (brd_active, 'preferences.profile.colors.relations.border-active', 1, 4, 'Relation'),
            (brd_spouse, 'preferences.profile.colors.relations.border-spouse', 2, 4, 'Relation'),
            (brd_father, 'preferences.profile.colors.relations.border-father', 3, 4, 'Relation'),
            (brd_mother, 'preferences.profile.colors.relations.border-mother', 4, 4, 'Relation'),
            (brd_brother, 'preferences.profile.colors.relations.border-brother', 5, 4, 'Relation'),
            (brd_sister, 'preferences.profile.colors.relations.border-sister', 6, 4, 'Relation'),
            (brd_son, 'preferences.profile.colors.relations.border-son', 7, 4, 'Relation'),
            (brd_daughter, 'preferences.profile.colors.relations.border-daughter', 8, 4, 'Relation'),
            (brd_none, 'preferences.profile.colors.relations.border-none', 9, 4, 'Relation'),

            # for event category scheme
            (bg_vital, 'preferences.profile.colors.events.vital', 1, 1, 'Event'),
            (bg_family, 'preferences.profile.colors.events.family', 2, 1, 'Event'),
            (bg_religious, 'preferences.profile.colors.events.religious', 3, 1, 'Event'),
            (bg_vocational, 'preferences.profile.colors.events.vocational', 4, 1, 'Event'),
            (bg_academic, 'preferences.profile.colors.events.academic', 5, 1, 'Event'),
            (bg_travel, 'preferences.profile.colors.events.travel', 6, 1, 'Event'),
            (bg_legal, 'preferences.profile.colors.events.legal', 7, 1, 'Event'),
            (bg_residence, 'preferences.profile.colors.events.residence', 8, 1, 'Event'),
            (bg_other, 'preferences.profile.colors.events.other', 9, 1, 'Event'),
            (bg_custom, 'preferences.profile.colors.events.custom', 10, 1, 'Event'),
            (brd_vital, 'preferences.profile.colors.events.border-vital', 1, 4, 'Event'),
            (brd_family, 'preferences.profile.colors.events.border-family', 2, 4, 'Event'),
            (brd_religious, 'preferences.profile.colors.events.border-religious', 3, 4, 'Event'),
            (brd_vocational, 'preferences.profile.colors.events.border-vocational', 4, 4, 'Event'),
            (brd_academic, 'preferences.profile.colors.events.border-academic', 5, 4, 'Event'),
            (brd_travel, 'preferences.profile.colors.events.border-travel', 6, 4, 'Event'),
            (brd_legal, 'preferences.profile.colors.events.border-legal', 7, 4, 'Event'),
            (brd_residence, 'preferences.profile.colors.events.border-residence', 8, 4, 'Event'),
            (brd_other, 'preferences.profile.colors.events.border-other', 9, 4, 'Event'),
            (brd_custom, 'preferences.profile.colors.events.border-custom', 10, 4, 'Event'),
            ]

        # prepare scrolled window for colors settings
        scroll_window = Gtk.ScrolledWindow()
        colors_grid = self.create_grid()
        scroll_window.add(colors_grid)
        scroll_window.set_vexpand(True)
        scroll_window.set_policy(Gtk.PolicyType.NEVER,
                                 Gtk.PolicyType.AUTOMATIC)
        grid.attach(scroll_window, 0, 3, 7, 1)

        # add color settings to scrolled window by groups
        row = 0
        self.colors = {}
        for key, frame_lbl in color_type.items():
            group_label = Gtk.Label()
            group_label.set_halign(Gtk.Align.START)
            group_label.set_margin_top(12)
            group_label.set_markup(_('<b>%s</b>') % frame_lbl)
            colors_grid.attach(group_label, 0, row, 3, 1)

            row_added = 0
            for color in color_list:
                if color[4] == key:
                    pref_name = color[1]
                    self.colors[pref_name] = self.add_color(
                        colors_grid, color[0], row + color[2],
                        pref_name, col=color[3])
                    row_added += 1
            row += row_added + 1

        return _('Colors'), grid

    def add_color(self, grid, label, index, constant, col=0):
        """
        Add color chooser widget with label and hex value to the grid.
        """
        lwidget = BasicLabel(_("%s: ") % label)  # needed for French
        colors = self._config.get(constant)
        if isinstance(colors, list):
            scheme = config.get('colors.scheme')
            hexval = colors[scheme]
        else:
            hexval = colors
        color = Gdk.color_parse(hexval)
        entry = Gtk.ColorButton(color=color)
        color_hex_label = BasicLabel(hexval)
        color_hex_label.set_hexpand(True)
        entry.connect('notify::color', self.update_color, constant,
                      color_hex_label)
        grid.attach(lwidget, col, index, 1, 1)
        grid.attach(entry, col+1, index, 1, 1)
        grid.attach(color_hex_label, col+2, index, 1, 1)
        return entry

    def update_color(self, obj, pspec, constant, color_hex_label):
        """
        Called on changing some color.
        Either on programmatically color change.
        """
        rgba = obj.get_rgba()
        hexval = "#%02x%02x%02x" % (int(rgba.red * 255),
                                    int(rgba.green * 255),
                                    int(rgba.blue * 255))
        color_hex_label.set_text(hexval)
        colors = self._config.get(constant)
        if isinstance(colors, list):
            scheme = config.get('colors.scheme')
            colors[scheme] = hexval
            self._config.set(constant, colors)
        else:
            self._config.set(constant, hexval)

    def _get_configure_page_funcs(self):
        """
        Return a list of functions that create gtk elements to use in the
        notebook pages of the Configure dialog

        :return: list of functions
        """
        return [
            self.layout_panel,
            self.color_panel,
            self.active_panel,
            self.parents_panel,
            self.siblings_panel,
            self.spouses_panel,
            self.children_panel,
            self.timeline_panel,
            self.citations_panel,
        ]

    def edit_active(self, *obj):
        if self.active_profile:
            self.active_profile.edit_object()

    def add_spouse(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_spouse()

    def select_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_existing_parents()

    def add_parents(self, *obj):
        if self.active_profile:
            self.active_profile.add_new_parents()

    def add_tag(self, trans, object_handle, tag_handle):
        if self.active_profile:
            self.active_profile.add_tag(trans, object_handle, tag_handle)
