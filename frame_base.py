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

"""
BaseProfile
"""

import time

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk, Gdk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gui.editors import EditPerson, EditFamily, EditEvent, EditCitation
from gramps.gen.lib import EventType, Person, Family, Event, Citation, Span
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.display.name import displayer as name_displayer
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.utils.alive import probably_alive
from gramps.gen.utils.thumbnails import get_thumbnail_image
from gramps.gen.utils.file import media_path_full
from gramps.gui.utils import open_file_with_default_application


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_utils import (
    _GENDERS, get_relation, get_key_person_events, format_date_string, TextLink
    )

try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext


_EDITORS = {
    "Person": EditPerson,
    "Family": EditFamily,
    "Event": EditEvent,
    "Citation": EditCitation
}


# ------------------------------------------------------------------------
#
# BaseProfile class
#
# ------------------------------------------------------------------------
class BaseProfile():
    """
    The BaseProfile class provides some basic services for profile construction
    and management.
    """

    def __init__(self, dbstate, uistate, space, config, router):
        self.dbstate = dbstate
        self.uistate = uistate
        self.obj = None
        self.image = None
        self.router = router
        self.config = config
        self.space = space
        self.facts_grid = Gtk.Grid(row_spacing=2, column_spacing=6)
        self.facts_row = 0
        self.enable_tooltips = self.config.get("{}.layout.enable-tooltips".format(self.space))
        self.markup = "{}"
        if self.config.get("{}.layout.use-smaller-detail-font".format(self.space)):
            self.markup = "<small>{}</small>"

    def option(self, context, name):
        try:
            return self.config.get("{}.{}.{}".format(self.space, context, name))
        except AttributeError:
            return False

    def make_label(self, text, left=True):
        if left:
            label = Gtk.Label(hexpand=False, halign=Gtk.Align.START, justify=Gtk.Justification.LEFT, wrap=True)
        else:
            label = Gtk.Label(hexpand=False, halign=Gtk.Align.END, justify=Gtk.Justification.RIGHT, wrap=True)
        label.set_markup(self.markup.format(text))
        return label
    
    def load_image(self):
        self.image = ImageFrame(self.dbstate.db, self.uistate, self.obj, size=bool(self.option(self.context, "show-image-large")))
        
    def add_event(self, event, reference=None, show_age=False):
        if event:
            age = None
            if show_age:
                span = Span(reference.date, event.date)
                if span.is_valid():
                    precision=global_config.get("preferences.age-display-precision")
                    age = str(span.format(precision=precision))
                if age == "unknown":
                    age = None

            event_format = self.config.get("{}.{}.event-format".format(self.space, self.context))
            if event_format in [3, 4, 6]:
                name = event.type.get_abbreviation(trans_text=glocale.translation.sgettext)
            else:
                name = glocale.translation.sgettext(event.type.xml_str())

            date = glocale.date_displayer.display(event.date)
            place = place_displayer.display_event(self.dbstate.db, event)

            text = ""
            if event_format in [1, 2, 5]:
                name_label = self.make_label(name)
            else:
                if event_format in [3, 4, 6]:
                    text = name

            if date:
                text = "{} {}".format(text, date).strip()

            if event_format in [1, 3]:
                if place:
                    text = "{} {} {}".format(text, _("in"), place).strip()

            if reference and age:
                text = "{} {}".format(text, age)

            if event_format in [1, 2]:
                text_label = self.make_label(text)
                self.facts_grid.attach(name_label, 0, self.facts_row, 1, 1)
                self.facts_grid.attach(text_label, 1, self.facts_row, 1, 1)
                self.facts_row = self.facts_row + 1                
            elif event_format in [3, 4]:
                text_label = self.make_label(text)
                self.facts_grid.attach(text_label, 0, self.facts_row, 1, 1)
                self.facts_row = self.facts_row + 1
            elif event_format in [5]:
                self.facts_grid.attach(name_label, 0, self.facts_row, 1, 1)
                if date:
                    if reference and age:
                        date_label = self.make_label("{} {}".format(date, age))
                    else:
                        date_label = self.make_label(date)
                    self.facts_grid.attach(date_label, 1, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1
                if place:
                    place_label = self.make_label(place)
                    self.facts_grid.attach(place_label, 1, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1
            elif event_format in [6]:
                if date:
                    if reference and age:
                        date_label = self.make_label("{} {} {}".format(name, date, age))
                    else:
                        date_label = self.make_label("{} {}".format(name, date))
                    self.facts_grid.attach(date_label, 0, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1
                if place:
                    if not date:
                        place_label = self.make_label("{} {}".format(name, place))
                    else:
                        place_label = self.make_label(place)
                    self.facts_grid.attach(place_label, 0, self.facts_row, 1, 1)
                    self.facts_row = self.facts_row + 1

    def object_type(self):
        if isinstance(self.obj, Person):
            return "Person"
        if isinstance(self.obj, Family):
            return "Family"
        if isinstance(self.obj, Event):
            return "Event"
        if isinstance(self.obj, Citation):
            return "Citation"

    def get_gramps_id_label(self):
        label = Gtk.Label(use_markup=True, label=self.markup.format(self.obj.gramps_id))
        hbox = Gtk.HBox()
        hbox.pack_end(label, False, False, 0)
        if self.obj.private:
            image = Gtk.Image()
            image.set_from_icon_name("gramps-lock", Gtk.IconSize.BUTTON)
            hbox.pack_end(image, False, False, 0)
        return hbox

    def get_tags_flowbox(self):
        tag_mode = self.option(self.context, "tag-format")
        if not tag_mode:
            return None
        tag_width = self.option(self.context, "tag-width")
        flowbox = Gtk.FlowBox(min_children_per_line=tag_width, max_children_per_line=tag_width)
        tags = []
        for handle in self.obj.get_tag_list():
            tag = self.dbstate.db.get_tag_from_handle(handle)
            tags.append((tag.priority, tag.name, tag.color))
        tags.sort()
        for tag in tags:
            color = Gdk.RGBA()
            color.parse(tag[2])
            if tag_mode == 1:
                tag_view = Gtk.Image()
                tag_view.set_from_icon_name("gramps-tag", Gtk.IconSize.BUTTON)
                tag_view.set_tooltip_text(tag[1])
                css = '.image {{ margin: 0px; padding: 0px; background-image: none; background-color: {}; }}'.format(tag[2][:7])
                css_class = 'image'
            else:
                tag_view = Gtk.Label(label=tag[1])
                css = ".label {{ margin: 0px; padding: 0px; font-size: x-small; color: black; background-color: {}; }}".format(tag[2][:7])
                css_class = 'label'
            css = css.encode('utf-8')
            provider = Gtk.CssProvider()
            provider.load_from_data(css)
            context = tag_view.get_style_context()
            context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            context.add_class(css_class)
            flowbox.add(tag_view)
        flowbox.show_all()
        return flowbox
    
    def build_action_menu(self, obj, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.action_menu = Gtk.Menu()
            self.action_menu.append(self._edit_object_option())
            self.add_custom_actions()
            add_tag_option = self._add_tag_option()
            if add_tag_option:
                self.action_menu.append(add_tag_option)
            remove_tag_option = self._remove_tag_option()
            if remove_tag_option:
                self.action_menu.append(remove_tag_option)
            self.action_menu.append(self._change_privacy_option())
            
            if self.obj.change:
                text = "{} {}".format(_("Last changed"), time.strftime('%x %X', time.localtime(self.obj.change)))
            else:
                text = _("Never changed")
            label = Gtk.MenuItem(label=text)
            self.action_menu.append(label)
            
            self.action_menu.show_all()
            if Gtk.get_minor_version() >= 22:
                self.action_menu.popup_at_pointer(event)
            else:
                self.action_menu.popup(None, None, None, None,
                                       event.button, event.time)

    def add_custom_actions(self):
        pass
    
    def _edit_object_option(self):
        if self.object_type() == "Person":
            name = _("Edit %s") % name_displayer.display(self.obj)
        else:
            name = _("Edit {}".format(self.object_type()))
        image = Gtk.Image.new_from_icon_name('gtk-edit', Gtk.IconSize.MENU)
        item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=name)
        item.connect('activate', self.edit_object)
        return item

    def edit_object(self, *obj):
        try:
            _EDITORS[self.object_type()](self.dbstate, self.uistate, [], self.obj)
        except WindowActiveError:
            pass

    def _change_privacy_option(self):
        if self.obj.private:
            image = Gtk.Image.new_from_icon_name('gramps-unlock', Gtk.IconSize.MENU)
            item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Make public"))
            item.connect('activate', self.change_privacy, False)
        else:
            image = Gtk.Image.new_from_icon_name('gramps-lock', Gtk.IconSize.MENU)
            item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Make private"))
            item.connect('activate', self.change_privacy, True)
        return item

    def change_privacy(self, obj, mode):
        object_type = self.object_type()
        commit_method = self.dbstate.db.method("commit_%s", object_type)
        with DbTxn(_("Change Privacy for %s") % object_type, self.dbstate.db) as trans:
            self.obj.set_privacy(mode)
            commit_method(self.obj, trans)
        
    def _add_tag_option(self):
        """
        If applicable generate menu option for tag addition.
        """
        tag_menu = None
        for handle in self.dbstate.db.get_tag_handles():
            if handle not in self.obj.tag_list:
                if not tag_menu:
                    tag_menu = Gtk.Menu()
                tag = self.dbstate.db.get_tag_from_handle(handle)
                image = Gtk.Image.new_from_icon_name('gramps-tag', Gtk.IconSize.MENU)
                tag_menu_item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=tag.name)
                tag_menu.add(tag_menu_item)
                tag_menu_item.connect("activate", self.add_tag, tag.handle)
        if tag_menu:
            image = Gtk.Image.new_from_icon_name('gramps-tag', Gtk.IconSize.MENU)        
            item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Add Tag"))
            item.set_submenu(tag_menu)
            return item
        return None
        
    def add_tag(self, obj, handle):
        """
        Add the given tag to the active object.
        """
        object_type = self.object_type()
        commit_method = self.dbstate.db.method("commit_%s", object_type)
        with DbTxn(_("Add Tag to %s") % object_type, self.dbstate.db) as trans:
            self.obj.add_tag(handle)
            commit_method(self.obj, trans)
        
    def _remove_tag_option(self):
        """
        If applicable generate menu option for tag removal.
        """
        tag_menu = None
        for handle in self.dbstate.db.get_tag_handles():
            if handle in self.obj.tag_list:
                if not tag_menu:
                    tag_menu = Gtk.Menu()
                tag = self.dbstate.db.get_tag_from_handle(handle)
                image = Gtk.Image.new_from_icon_name('gramps-tag', Gtk.IconSize.MENU)
                tag_menu_item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=tag.name)
                tag_menu.add(tag_menu_item)
                tag_menu_item.connect("activate", self.remove_tag, tag.handle)
        if tag_menu:
            image = Gtk.Image.new_from_icon_name('gramps-tag', Gtk.IconSize.MENU)        
            item = Gtk.ImageMenuItem(always_show_image=True, image=image, label=_("Remove Tag"))
            item.set_submenu(tag_menu)
            return item
        return None
        
    def remove_tag(self, obj, handle):
        """
        Remove the given tag for the person."
        """
        object_type = self.object_type()
        commit_method = self.dbstate.db.method("commit_%s", object_type)
        with DbTxn(_("Remove Tag from %s") % object_type, self.dbstate.db) as trans:
            self.obj.remove_tag(handle)
            commit_method(self.obj, trans)

    
    def set_css_style(self):
        """
        Add styling to a frame object.
        """
        border = self.option("layout", "border-width")
        color = self._get_color_string()
        css = ".frame {{ border-width: {}px; {} }}".format(border, color)
        css = css.encode('utf-8')
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        if isinstance(self, Gtk.Frame):
            context = self.get_style_context()
        elif hasattr(self, "frame"):
            context = self.frame.get_style_context()
        else:
            return
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        context.add_class("frame")


    def _get_color_string(self):
        """
        Determine coloring scheme to be used if specified.
        """
        background_color = ""
        border_color = ""

        if isinstance(self.obj, Person):
            if not self.config.get("preferences.profile.person.layout.use-color-scheme"):
                return ""
            if self.obj.gender == Person.MALE:
                key = "male"
            elif self.obj.gender == Person.FEMALE:
                key = "female"
            else:
                key = "unknown"
            if self.living:
                value = "alive"
            else:
                value = "dead"
            border_color = global_config.get("colors.border-{}-{}".format(key, value))
            if self.relation and self.relation.handle == self.obj.handle:
                key = "home"
                value = "person"
            background_color = global_config.get("colors.{}-{}".format(key, value))

        if isinstance(self.obj, Family):
            if not self.config.get("preferences.profile.person.layout.use-color-scheme"):
                return ""
            background_color = global_config.get("colors.family")
            border_color = global_config.get("colors.border-family")
            if self.obj.type is not None or self.divorced is not None:
                key = self.obj.type.value
                if self.divorced is not None and self.divorced:
                    border_color = global_config.get("colors.border-family-divorced")
                    key = 99
                values = {
                    0: "-married",
                    1: "-unmarried",
                    2: "-civil-union",
                    3: "-unknown",
                    4: "",
                    99: "-divorced"
                }
                background_color = global_config.get("colors.family{}".format(values[key]))

        scheme = global_config.get("colors.scheme")
        css = ""
        if background_color:
            css = 'background-color: {};'.format(background_color[scheme])
        if border_color:
            css = '{} border-color: {};'.format(css, border_color[scheme])
        return css



class ImageFrame(Gtk.Frame):
    """
    Simple class for managing display of an image.
    """

    def __init__(self, db, uistate, obj, size=0):
        Gtk.Frame.__init__(self, expand=False, shadow_type=Gtk.ShadowType.NONE)
        self.db = db
        self.uistate = uistate
        media = obj.get_media_list()
        if media:
            thumbnail = self.get_thumbnail(media[0], size)
            if thumbnail:
                self.add(thumbnail)

    def get_thumbnail(self, media_ref, size):
        mobj = self.db.get_media_from_handle(media_ref.ref)
        if mobj and mobj.get_mime_type()[0:5] == "image":
            pixbuf = get_thumbnail_image(
                media_path_full(self.db, mobj.get_path()),
                rectangle=media_ref.get_rectangle(),
                size=size)
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
            button = Gtk.Button(relief=Gtk.ReliefStyle.NONE)
            button.add(image)
            button.connect("clicked", lambda obj: self.view_photo(mobj))
            button.show_all()
            return button
        return None

    def view_photo(self, photo):
        """
        Open this picture in the default picture viewer.
        """
        photo_path = media_path_full(self.db, photo.get_path())
        open_file_with_default_application(photo_path, self.uistate)
