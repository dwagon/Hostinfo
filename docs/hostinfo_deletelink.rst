hostinfo_deletelink
===================

Delete a link from the hostinfo database::

    % hostinfo_deletelink [-h] [--everytag] [--tag TAG] host

* Options are:
    * ``--everylink`` - delete every tag and link for a host
    * ``--tag TAG`` - delete just the link with the appropriate tag
* Otherwise you must specify the tag of the link you are deleting
* There is no undo or confirmation required so be careful

New in version 1.21
