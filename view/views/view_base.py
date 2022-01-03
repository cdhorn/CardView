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
GrampsObjectView
"""
from abc import abstractmethod

# -------------------------------------------------------------------------
#
# GTK Modules
#
# -------------------------------------------------------------------------
from gi.repository import Gtk

# -------------------------------------------------------------------------
#
# Gramps Modules
#
# -------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Plugin Modules
#
# -------------------------------------------------------------------------
from ..bars.bar_media import MediaBarGroup
from ..common.common_const import GROUP_LABELS
from ..common.common_utils import make_scrollable
from ..groups.group_builder import group_builder

_ = glocale.translation.sgettext


class GrampsObjectView(Gtk.VBox):
    """
    Provides functionality common to all object views.
    """

    def __init__(self, grstate, grcontext):
        Gtk.VBox.__init__(
            self, hexpand=True, vexpand=False, spacing=3, border_width=3
        )
        self.grstate = grstate
        self.grcontext = grcontext
        self.view_header = Gtk.VBox(spacing=3)
        self.view_body = Gtk.HBox()
        self.view_object = None
        self.view_focus = None
        self.render_view()

    def render_view(self):
        """
        Render the view after building it.
        """
        self.build_view()
        mode = self.grstate.config.get("options.global.media-bar.position")
        if mode in [0]:
            self.render_view_body(self, mode)
        else:
            wrapper = Gtk.HBox(spacing=1)
            if mode in [1]:
                self.add_media_bar(wrapper, self.grcontext.primary_obj.obj)
                vbox = Gtk.VBox()
                self.render_view_body(vbox, mode)
                wrapper.pack_start(vbox, True, True, 0)
            else:
                vbox = Gtk.VBox()
                self.render_view_body(vbox, mode)
                wrapper.pack_start(vbox, True, True, 0)
                self.add_media_bar(wrapper, self.grcontext.primary_obj.obj)
            self.pack_start(wrapper, True, True, 0)
        self.show_all()

    def render_view_body(self, widget, mode):
        """
        Render main body of the view.
        """
        if self.grstate.config.get("options.global.display.pin-header"):
            widget.pack_start(self.view_header, False, False, 0)
            if mode == 0:
                self.add_media_bar(widget, self.grcontext.primary_obj.obj)
            scrollable_body = make_scrollable(self.view_body)
            scrollable_body.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )
            widget.pack_end(scrollable_body, True, True, 0)
        else:
            body = Gtk.VBox()
            body.pack_start(self.view_header, False, False, 0)
            if mode == 0:
                self.add_media_bar(body, self.grcontext.primary_obj.obj)
            body.pack_end(self.view_body, True, True, 0)
            scrollable_body = make_scrollable(body)
            scrollable_body.set_policy(
                Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
            )
            widget.pack_start(scrollable_body, True, True, 0)

    @abstractmethod
    def build_view(self):
        """
        Build the view header and body and set the focus.
        """
        raise NotImplementedError

    def wrap_focal_widget(self, focal_widget):
        """
        Wrap focal widget with colored background so it stands out.
        """
        if not self.grstate.config.get(
            "options.global.display.focal-object-highlight"
        ):
            return focal_widget
        scheme = global_config.get("colors.scheme")
        background = self.grstate.config.get(
            "options.global.display.focal-object-color"
        )
        frame = Gtk.Frame()
        css = "".join(
            (
                ".frame { border: 0px; padding: 3px; ",
                "background-image: none; background-color: ",
                background[scheme],
                "; }",
            )
        )
        css = css.encode("utf-8")
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        context = frame.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")
        frame.add(focal_widget)
        return frame

    def build_object_groups(self, gramps_obj, age_base=None):
        """
        Gather and build the object groups.
        """
        option = ".".join(
            ("options.page", gramps_obj.obj_type.lower(), "layout.groups")
        )
        group_list = self.grstate.config.get(option).split(",")
        object_groups = self.get_object_groups(
            group_list, gramps_obj.obj, age_base=age_base
        )
        return self.render_group_view(object_groups)

    def get_object_groups(self, group_list, obj, age_base=None):
        """
        Gather the object groups.
        """
        args = {"page_type": self.grcontext.page_type.lower()}
        if age_base:
            args["age_base"] = age_base
        object_groups = {}
        for key in group_list:
            object_groups.update(
                {key: group_builder(self.grstate, key, obj, args)}
            )
        return object_groups

    def render_group_view(self, obj_groups):
        """
        Identify format for the group view and call method to prepare it.
        """
        space = "".join(
            ("options.page.", self.grcontext.page_type.lower(), ".layout")
        )
        groups = self.grstate.config.get("".join((space, ".groups"))).split(
            ","
        )
        scrolled = self.grstate.config.get("".join((space, ".scrolled")))
        groupings = []
        current_grouping = []
        for group in groups:
            if (
                self.grstate.config.get(
                    "".join((space, ".", group, ".visible"))
                )
                and group in obj_groups
                and obj_groups[group]
            ):
                current_grouping.append(group)
            if (
                not self.grstate.config.get(
                    "".join((space, ".", group, ".append"))
                )
                and current_grouping
            ):
                groupings.append(current_grouping)
                current_grouping = []
        if current_grouping:
            groupings.append(current_grouping)
        if self.grstate.config.get("".join((space, ".tabbed"))):
            return prepare_tabbed_groups(obj_groups, groupings, scrolled)
        return prepare_untabbed_groups(obj_groups, groupings, scrolled)

    def add_media_bar(self, widget, obj):
        """
        Check and if need and can build media bar add to widget for viewing.
        """
        if self.grstate.config.get("options.global.media-bar.enabled"):
            css = self.view_object.get_css_style()
            mediabar = MediaBarGroup(self.grstate, None, obj, css=css)
            if mediabar.total:
                widget.pack_start(mediabar, False, False, 0)


def add_to_title(title, group):
    """
    Add group label to title.
    """
    if not title:
        title = GROUP_LABELS[group]
    else:
        if " & " in title:
            title = title.replace(" &", ",")
        title = "".join((title, " & ", GROUP_LABELS[group]))
    return title


def pack_container(container, scrolled, box):
    """
    Pack container with widget.
    """
    if scrolled:
        container.pack_start(
            make_scrollable(box, vexpand=False, hexpand=True),
            expand=False,
            fill=True,
            padding=0,
        )
    else:
        container.pack_start(box, expand=False, fill=True, padding=0)


def prepare_untabbed_groups(obj_groups, groupings, scrolled):
    """
    Generate the untabbed full page view for the groups.
    """
    container = Gtk.HBox(spacing=3, hexpand=True, vexpand=False)
    for grouping in groupings:
        if len(grouping) == 1:
            pack_container(container, scrolled, obj_groups[grouping[0]])
        else:
            box = Gtk.VBox(spacing=3, vexpand=False)
            for group in grouping:
                box.pack_start(
                    obj_groups[group], expand=False, fill=True, padding=0
                )
            pack_container(container, scrolled, box)
    return container


def prepare_tabbed_groups(obj_groups, groupings, scrolled):
    """
    Generate the tabbed notebook view for the groups.
    """
    notebook = Gtk.Notebook()
    for grouping in groupings:
        title = ""
        if len(grouping) == 1:
            label = Gtk.Label(label=add_to_title(title, grouping[0]))
            notebook.append_page(
                make_scrollable(obj_groups[grouping[0]]), tab_label=label
            )
        else:
            box = Gtk.HBox(spacing=3, vexpand=False)
            for group in grouping:
                title = add_to_title(title, group)
                pack_container(box, scrolled, obj_groups[group])
            label = Gtk.Label(label=title)
            notebook.append_page(
                make_scrollable(box, vexpand=False), tab_label=label
            )
    return notebook
