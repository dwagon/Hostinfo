hostinfo_deletelink
===================

Delete an link from the hostinfo database::

    % hostinfo_deletelink --everylink|tag hostname

* Options are:
    * ``--everylink`` - delete every link for a host
* Otherwise you must specify the tag of the link you are deleting
* There is no undo or confirmation required so be careful

New in version 1.21
