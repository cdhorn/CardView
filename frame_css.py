#
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
ProfileFrame CSS support routines
"""

# ------------------------------------------------------------------------
#
# GTK modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk


# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.config import config as global_config
from gramps.gen.lib import EventType, Person, Family, FamilyRelType, Citation


# ------------------------------------------------------------------------
#
# Plugin modules
#
# ------------------------------------------------------------------------
from frame_image import ImageFrame


def add_style(obj, css, name):
    """
    Add styling to a single object.
    """
    css = css.encode('utf-8')
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    if isinstance(obj, Gtk.Frame):
        context = obj.get_style_context()
    elif hasattr(obj, "frame"):
        context = obj.frame.get_style_context()
    else:
        return
    context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    context.add_class(name)


def add_style_single_frame(obj):
    """
    Add styling to a single frame object.
    """
    thick_border=False
    if hasattr(obj, "config"):
        if obj.config.get("preferences.profile.layout.use-thick-borders"):
            thick_border = True
    border = get_border_string(thick_borders=thick_border)
    color = get_color_string(obj)
    css = ".frame {{ {} {} }}".format(border, color)
    add_style(obj, css, "frame")
    

def add_style_double_frame(obj1, obj2):
    """
    Add styling to two side by side frames objects such that no border
    appears between them so they appear as if one.
    """
    thick_border = False
    if hasattr(obj1, "config"):
        if obj1.config.get("preferences.profile.layout.use-thick-borders"):
            thick_border = True
    elif hasattr(obj2, "config"):
        if obj2.config.get("preferences.profile.layout.use-thick-borders"):
            thick_border = True
    obj1_border = get_border_string(thick_borders=thick_border, right_open=True)
    obj2_border = get_border_string(thick_borders=thick_border, left_open=True)
    if isinstance(obj1, ImageFrame):
        color = get_color_string(obj2)
    else:
        color = get_color_string(obj1)
    css = ".frame {{ {} {} }}".format(obj1_border, color)
    add_style(obj1, css, "frame")
    css = ".frame {{ {} {} }}".format(obj2_border, color)
    add_style(obj2, css, "frame")
    
    
def get_border_string(thick_borders=True, left_open=False, right_open=False):
    """
    Generate border styling string.
    """
    css = 'border-top-width: {}px; border-bottom-width: {}px; border-left-width: {}px; border-right-width: {}px;'
    border = 2
    if thick_borders:
        border = 3
    left = border
    right = border
    if left_open:
        left = 0
    if right_open:
        right = 0
    return css.format(border, border, left, right)

    
def get_color_string(obj):
    """
    Probes a PersonProfileFrame or FamilyProfileFrame object to determine colors to use.
    """
    background_color = ""
    border_color = ""

    if hasattr(obj, "person") and isinstance(obj.person, Person):
        if hasattr(obj, "config") and obj.config.get("preferences.profile.person.layout.use-color-scheme"):
            if obj.person.gender == Person.MALE:
                key = "male"
            elif obj.person.gender == Person.FEMALE:
                key = "female"
            else:
                key = "unknown"
            if obj.living:
                value = "alive"
            else:
                value = "dead"
            border_color = global_config.get("colors.border-{}-{}".format(key, value))
            if obj.relation and obj.relation.handle == obj.person.handle:
                key = "home"
                value = "person"
            background_color = global_config.get("colors.{}-{}".format(key, value))

    if hasattr(obj, "family") and isinstance(obj.family, Family):
        if hasattr(obj, "config") and obj.config.get("preferences.profile.person.layout.use-color-scheme"):        
            background_color = global_config.get("colors.family")
            border_color = global_config.get("colors.border-family")
            if obj.family.type is not None or obj.divorced is not None:
                key = obj.family.type.value
                if obj.divorced is not None and obj.divorced:
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
