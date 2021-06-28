# Gramps ProfileView Plugin

This plugin is an experimental effort to provide an alternate person view, a "Person Profile" view so to speak, for [Gramps](https://gramps-project.org)  It is largely modelled after the layout styles used by many online genealogy sites. It is hoped that it may provide an easier to navigate view for Gramps newcomers.

This is still in a development phase as I toy around with it but far enough along it should be fairly usable.

Be sure to backup your tree or use a copy of it if exploring the functionality. Note a number of plugin ini configuration file options have changed format a couple times, if you have trouble and suspect that may be the cause it is best to remove the People_personprofile.ini for it to be recreated.  Also note that while most options are global and fixed across trees that a subset of them are now tree specific if they are changed.

## Installation
        
As a Gramps plugin it can simply be installed by creating a plugin subdirectory ~/.gramps/gramps51/plugins/ProfileView and copying the files into place.

## Usage Notes

Fairly straight forward, click on people names to navigate the tree like the other relationship views which served as a foundation for it. Right clicking on any frame will present a drop down action menu. Some of the available actions will vary based on the context of the object, so options for the active person in the header will differ from those for a parent or spouse or child or event or cited source. A large number of them are common to all objects.

As I work with a pair of large high resolution monitors I have not focused on how it might look on a low resolution display. Given the amount of information it can show probably not well.  However I have strived to make it as configurable as possible for an end user so the many configuration options for the view should be reviewed. These allow it to be tairlored for smaller displays to a point.

## History

This started as a Gramplet to learn about Gtk and toy around a bit. The Combined view served as a model when I decided to do more with it and try to create a view instead. I then refactored it to use the original NavigationView class. Most of the code in person_profile.py and frame_base.py derived from the work of other Gramps developers to whom I am indebted.

