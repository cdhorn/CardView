![CardView icon](icons/gramps-relation-linked.svg) Card View Addon Known Issues
===============

Below are some known common issues with this collection of Addons to be aware of.


### AttributeError: 'NoneType' object has no attribute 'post_create'

In certain scenarios on startup when switching databases or trying to navigate you may see the following:

```
186123: ERROR: grampsapp.py: line 174: Unhandled exception
Traceback (most recent call last):
File "Z:\PortableApps\GrampsPortable\App\Gramps\gramps\gui\navigator.py", line 274, in cb_view_clicked
self.viewmanager.goto_page(int(cat_num), int(view_num))
File "Z:\PortableApps\GrampsPortable\App\Gramps\gramps\gui\viewmanager.py", line 786, in goto_page
self.__create_page(page_def[0], page_def[1])
File "Z:\PortableApps\GrampsPortable\App\Gramps\gramps\gui\viewmanager.py", line 840, in __create_page
self.active_page.post_create()
AttributeError: 'NoneType' object has no attribute 'post_create'
```

The page is not available but it tries to run the post_create() method anyway.
