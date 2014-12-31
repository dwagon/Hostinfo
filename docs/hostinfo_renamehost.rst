hostinfo_renamehost
===================

Rename a host in the hostinfo database. All data associated with the srchost will now be associated with the dsthost.::

    % hostinfo_renamehost --src <srchost> --dst <dsthost>

* The dsthost can't exist beforehand
* Obviously the srchost has to exist
