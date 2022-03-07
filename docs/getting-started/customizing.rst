Customizing LLEMR
=================

The Admin Panel
---------------

The majority of customization of an LLEMR instance can be achieved by using the admin panel, found at `/admin`, availiable to any user with staff status. Common customizations include:

* Almost every drop-down list can be customized on the admin panel
* Add/change user groups (typically attendings, volunteers, etc.)

.. warning::
    It is possible, although a little challenging, to destroy data or place your instance in a broken state through the admin panel. You can almost always rescue the situation (with backups or a good understanding of the `manage.py shell` interface). Still, you want to avoid:

    * deleting models that are extensively referenced by other models
    * deleting all of a particular type of model (for instance, if there are no Gender objects, no new patients can be created).


Django Variables
----------------

Some site-wide customizations, like which apps are active, upper and lower limits for the systolic blood pressure, among other things, are controlled as Django settings. These are edited in the appropriate settings file.
