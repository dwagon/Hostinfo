hostinfo_deletehost
===================

Delete a host from the hostinfo database::

    % hostinfo_deletehost [--lethal] <host>

* This will remove a single host (deliberately not multiple hosts) and all of its associated data
* It will also delete all of the aliases that point to this host
* The deletion will only occur if the ``--lethal`` flag is specified, otherwise it will just tell you what it is going to do
* There is no coming back from this - so be careful
