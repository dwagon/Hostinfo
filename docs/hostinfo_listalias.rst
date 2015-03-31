hostinfo_listalias
==================

List the aliases of a host from the hostinfo database::

    % hostinfo_listalias host

* List all the ways that this host can be referred to
* If you add ``--all`` it will print out all the aliases that hostinfo knows about
* If it has no aliases it will just print out the real name and a return code of 1
* If it has aliases it will print out the real name followed by the aliases and a return code of 0
