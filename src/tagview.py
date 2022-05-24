# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2001-2006  Donald N. Allingham
# Copyright (C) 2008       Gary Burton
# Copyright (C) 2010       Nick Hall
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
Tag View.
"""

# -------------------------------------------------------------------------
#
# GTK/Gnome Modules
#
# -------------------------------------------------------------------------
from gi.repository import Gdk, Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.datehandler import format_time
from gramps.gui.views.listview import ListView, TEXT, MARKUP, ICON
from gramps.gui.views.treemodels.flatbasemodel import FlatBaseModel
from gramps.gen.errors import WindowActiveError
from gramps.gui.views.bookmarks import NoteBookmarks
from gramps.gen.config import config
from gramps.gen.lib import Tag
from gramps.gui.ddtargets import DdTargets
from gramps.gui.dialog import ErrorDialog, QuestionDialog
from gramps.gui.views.tags import EditTag
from gramps.gen.plug import CATEGORY_QR_NOTE
from gramps.gen.utils.string import data_recover_msg

_ = glocale.translation.sgettext

# HARD DEPENDENCY ON NON-GRAMPS CORE CODE
from view.actions.delete import delete_object


# Tags lack this like other primary objects so we construct our own
(POS_HANDLE, POS_NAME, POS_COLOR, POS_PRIORITY, POS_CHANGE) = list(range(5))

# -------------------------------------------------------------------------
#
# TagModel
#
# -------------------------------------------------------------------------
class TagModel(FlatBaseModel):
    """
    Basic model for a Tag list
    """

    def __init__(
        self,
        db,
        uistate,
        scol=0,
        order=Gtk.SortType.ASCENDING,
        search=None,
        skip=set(),
        sort_map=None,
    ):
        """Setup initial values for instance variables."""
        self.gen_cursor = db.get_tag_cursor
        self.map = db.get_raw_tag_data
        self.fmap = [
            self.column_handle,
            self.column_name,
            self.column_color,
            self.column_priority,
            self.column_change,
        ]
        self.smap = [
            self.column_handle,
            self.column_name,
            self.column_color,
            self.column_priority,
            self.column_change,
        ]
        FlatBaseModel.__init__(
            self,
            db,
            uistate,
            scol,
            order,
            search=search,
            skip=skip,
            sort_map=sort_map,
        )

    def destroy(self):
        """
        Unset all elements that can prevent garbage collection
        """
        self.db = None
        self.gen_cursor = None
        self.map = None
        self.fmap = None
        self.smap = None
        FlatBaseModel.destroy(self)

    def color_column(self):
        """
        Return the color column.
        """
        return 2

    def on_get_n_columns(self):
        """Return the column number of the Tag tab."""
        return len(self.fmap) + 1

    def column_handle(self, data):
        """Return the handle of the Tag."""
        return data[POS_HANDLE]

    def column_name(self, data):
        """Return the name of the Tag in readable format."""
        return data[POS_NAME]

    def column_priority(self, data):
        """Return the priority of the Tag."""
        return data[POS_PRIORITY]

    def column_color(self, data):
        return data[POS_COLOR]

    def sort_change(self, data):
        return "%012x" % data[POS_CHANGE]

    def column_change(self, data):
        return format_time(data[POS_CHANGE])


# -------------------------------------------------------------------------
#
# TagView
#
# This is very much hacked up to make it mostly work as a new ListView
# plugin without resorting to changes in Gramps core at this time...
#
# -------------------------------------------------------------------------
class TagView(ListView):
    """
    TagView, a normal flat listview for the tags
    """

    COL_NAME = 1
    COL_COLO = 2
    COL_PRIO = 3
    COL_CHAN = 4

    # column definitions
    COLUMNS = [
        (_("Handle"), TEXT, None),
        (_("Name"), TEXT, None),
        (_("Color"), TEXT, None),
        (_("Priority"), TEXT, None),
        (_("Last Changed"), TEXT, None),
    ]
    # default setting with visible columns, order of the col, and their size
    CONFIGSETTINGS = (
        ("columns.visible", [COL_NAME, COL_COLO, COL_PRIO, COL_CHAN]),
        ("columns.rank", [COL_NAME, COL_COLO, COL_PRIO, COL_CHAN]),
        ("columns.size", [350, 150, 100, 100]),
    )

    ADD_MSG = _("Add a new tag")
    EDIT_MSG = _("Edit the selected tag")
    DEL_MSG = _("Delete the selected tag")

    FILTER_TYPE = "Tag"
    QR_CATEGORY = CATEGORY_QR_NOTE

    def __init__(self, pdata, dbstate, uistate, nav_group=0):

        signal_map = {
            "tag-add": self.row_add,
            "tag-update": self.row_update,
            "tag-delete": self.row_delete,
            "tag-rebuild": self.object_build,
        }

        # Work around for modify_statusbar issues
        if "Tag" not in uistate.NAV2MES:
            uistate.NAV2MES["Tag"] = ""

        ListView.__init__(
            self,
            _("Tags"),
            pdata,
            dbstate,
            uistate,
            TagModel,
            signal_map,
            NoteBookmarks,
            nav_group,
            filter_class=None,
            multiple=False,
        )

        self.additional_uis.append(self.additional_ui)

    def navigation_type(self):
        return "Tag"

    def drag_info(self):
        """
        No tag drag type supported in Gramps core yet
        """
        return None

    def get_stock(self):
        """
        Use the gramps-tag stock icon
        """
        return "gramps-tag"

    additional_ui = [  # Defines the UI string for UIManager
        """
      <placeholder id="LocalExport">
        <item>
          <attribute name="action">win.ExportTab</attribute>
          <attribute name="label" translatable="yes">Export View...</attribute>
        </item>
      </placeholder>
""",
        """
      <placeholder id="CommonGo">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">_Forward</attribute>
        </item>
      </section>
      </placeholder>
""",
        """
      <section id='CommonEdit' groups='RW'>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
      </section>
"""
        % _(
            "_Edit...", "action"
        ),  # to use sgettext() # Following are the Toolbar items
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
    </placeholder>
""",
        """
    <placeholder id='BarCommonEdit'>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-add</property>
        <property name="action-name">win.Add</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Add...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">gtk-edit</property>
        <property name="action-name">win.Edit</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">Edit...</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    <child groups='RW'>
      <object class="GtkToolButton">
        <property name="icon-name">list-remove</property>
        <property name="action-name">win.Remove</property>
        <property name="tooltip_text">%s</property>
        <property name="label" translatable="yes">_Delete</property>
        <property name="use-underline">True</property>
      </object>
      <packing>
        <property name="homogeneous">False</property>
      </packing>
    </child>
    </placeholder>
"""
        % (ADD_MSG, EDIT_MSG, DEL_MSG),
        """
    <menu id="Popup">
      <section>
        <item>
          <attribute name="action">win.Back</attribute>
          <attribute name="label" translatable="yes">_Back</attribute>
        </item>
        <item>
          <attribute name="action">win.Forward</attribute>
          <attribute name="label" translatable="yes">Forward</attribute>
        </item>
      </section>
      <section id="PopUpTree">
      </section>
      <section>
        <item>
          <attribute name="action">win.Add</attribute>
          <attribute name="label" translatable="yes">_Add...</attribute>
        </item>
        <item>
          <attribute name="action">win.Edit</attribute>
          <attribute name="label">%s</attribute>
        </item>
        <item>
          <attribute name="action">win.Remove</attribute>
          <attribute name="label" translatable="yes">_Delete</attribute>
        </item>
      </section>
      <section>
        <placeholder id='QuickReport'>
        </placeholder>
      </section>
    </menu>
    """
        % _("_Edit...", "action"),  # to use sgettext()
    ]
    # Ideally scrap QuickReport in Popup Menu but if we do triggers bugs
    # in Gramps core...

    def set_active(self):
        ListView.set_active(self)
        self.uistate.viewmanager.tags.tag_disable()
        self.bookmarks.undisplay()

    def set_inactive(self):
        ListView.set_inactive(self)
        self.uistate.viewmanager.tags.tag_enable(update_menu=False)
        self.bookmarks.display()

    def get_handle_from_gramps_id(self, gid):
        return None

    def add(self, *obj):
        try:
            EditTag(self.dbstate.db, self.uistate, [], Tag())
        except WindowActiveError:
            pass

    def remove(self, *obj):
        handles = self.selected_handles()
        if handles:
            obj = self.dbstate.db.get_tag_from_handle(handles[0])
            msg1 = " ".join((_("Delete"), _("Tag"), obj.name))
            msg2 = _("Deleting item will remove it from the database.")
            msg2 = "%s %s" % (msg2, data_recover_msg)
            QuestionDialog(
                msg1,
                msg2,
                _("_Delete"),
                lambda: self.delete_object_response(
                    obj, parent=self.uistate.window
                ),
                parent=self.uistate.window,
            )

    def delete_object_response(self, obj, parent=None):
        msg = " ".join((_("Delete"), obj.name))
        delete_object(self.dbstate.db, obj.handle, "Tag", msg)

    def edit(self, *obj):
        for handle in self.selected_handles():
            tag = self.dbstate.db.get_tag_from_handle(handle)
            try:
                EditTag(self.dbstate.db, self.uistate, [], tag)
            except WindowActiveError:
                pass

    def merge(self, *obj):
        """
        Possibly implement someday, but not this day!
        """
        pass

    def tag_updated(self, handle_list):
        """
        Update tagged rows when a tag color changes.
        """
        pass

    def get_default_gramplets(self):
        """
        Define the default gramplets for the sidebar and bottombar.
        """
        return ((), ())

    def remove_object_from_handle(self):
        pass

    def update_mru_menu(self, *args, **kwargs):
        pass

    def row_changed(self, selection):
        """
        Called with a list selection is changed.

        Check the selected objects in the list and return those that have
        handles attached.  Set the active object to the first item in the
        list. If no row is selected, set the active object to None.
        """
        selected_ids = self.selected_handles()
        if len(selected_ids) > 0:
            # In certain cases the tree models do row updates which result in a
            # selection changed signal to a handle in progress of being
            # deleted.  In these cases we don't want to change the active to
            # non-existant handles.
            if hasattr(self.model, "dont_change_active"):
                if not self.model.dont_change_active:
                    self.change_active(selected_ids[0])
            else:
                self.change_active(selected_ids[0])

        if len(selected_ids) == 1:
            if self.drag_info():
                self.list.drag_source_set(
                    Gdk.ModifierType.BUTTON1_MASK,
                    [self.drag_info().target()],
                    Gdk.DragAction.COPY,
                )
        elif len(selected_ids) > 1:
            if self.drag_list_info():
                self.list.drag_source_set(
                    Gdk.ModifierType.BUTTON1_MASK,
                    [self.drag_list_info().target()],
                    Gdk.DragAction.COPY,
                )

        if self.uistate.viewmanager.active_page == self:
            if selected_ids:
                tag = self.dbstate.db.get_tag_from_handle(selected_ids[0])
                name = "".join(("[", _("Tag"), "] ", tag.name))
                self.uistate.status.pop(self.uistate.status_id)
                self.uistate.status.push(self.uistate.status_id, name)
