# Gramps Relationship View Profile Plugin

This plugin is an effort to provide an interface that can be used to navigate through and view most of the data in a [Gramps](https://gramps-project.org) database. It is largely modelled after the layout styles used by many online genealogy sites. It is hoped that it may provide an easier to navigate view for Gramps newcomers.

This is still in a development phase as I toy around with it but far enough along it should be fairly usable.

HOWEVER, be sure to backup your tree or even better use a copy of it if exploring the functionality.

Note a number of the ini configuration file options have changed format a few times now, most recently on August 8th 2021.  If you have trouble and suspect that may be the cause it is best to remove the `Relationships_profileview.ini` and let it be recreated.

## Installation
        
As a Gramps plugin it can be installed by creating a plugin subdirectory `~/.gramps/gramps51/plugins/ProfileView` and copying or cloning the full contents of this repository into place.

## Usage Notes

At the present time there are page views for each of the major Gramps objects: Person, Family, Event, Place, Citation, Source, Repository, Media and Notes. Some page views for secondary objects have also been added: Child Reference, Association or Person Reference, Name and Tag. Note I am considering Tag a secondary object as it like other secondary objects is not trackable in the navigation history.

Normally the record in the header frame is the active record for the page. Note for the Citation page the Source record is shown above the Citation record and for Families the primary parents of each partner are shown above the partners.

Note as you navigate you are switching context across the different objects. Some Gramplets are designed to only work with specific objects or views, so will likely have problems.  Different Navigation and History classes are used, derived from the ones used in the Combined View, so some behaviour will be different from stock Gramps.

You can navigate using most of the titles of the framed objects which are links.  You can also double left click on most of the viewable space on any frame where data is displayed to also switch to that object page.

Right clicking on any frame will present a drop down action menu. Some of the available actions will vary based on the context of the object, so options for the active person in the header may differ from those for a parent or spouse or child or event or cited source. A large number of them are common to all objects.

Note in some contexts, such as children, the frame will contain two objects, the top level person object for the child and the child reference tracking their membership in a specific family. The drop down action menu for the reference object will contain operations that apply to the reference not the primary object.

All configuration options and page layouts are handled in the same configuration dialog now.

The options for objects under active apply when the frame appears in the page header, those for objects under groups apply to those not in the page header.
    
For the layout configuration the default mode is single page, with various object groups beneath the header record. This is designed for large high resolution displays. You can stack one group on top of another if needed, set which groups will render, and also choose which will hide when collapsed. If collapsed you can not reopen them, but you can click the active header to force it to reload the page and they will appear again. There is now also a tabbed mode selection which will be more similar though not exactly the same as in the Combined View. In that mode stacking places groups side by side in the same tab and the hide option is ignored.

Make note of the ability to customize the displayed data in most of the frames as well if you choose. For people you can choose which events, facts, and attributes to display as well as choose to display additional relationship calculations. Note these user customizable field options are generally stored per tree as things like custom events or attributes may differ across trees.

Some drag and drop functionality has been implemented. You can reorder children in a family, drag blocks of text from a browser page and drop it on an object to create a note, or drag the url for a page and drop it on an object that has url support to add it. Note Firefox works fine, mileage may vary with other browsers.

## Bug Reports and Feature Requests

At the present time these can be submitted on Github. I am particulary interested in any ideas for alternate page layouts for objects that might work better than what I have come up with so far.

## History

This started as a Gramplet to learn about Gtk and toy around a bit. The framework provided by the Combined view serves as the underpinnings although it was extended to apply to all object types. Several other large pieces of code are also derived from the work of other Gramps developers to whom I am indebted.
