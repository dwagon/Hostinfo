hostinfo_deletevalue
====================

Delete a value from hosts in the hostinfo database::

    % hostinfo_deletevalue <key>[=<value>] <host> [<host>...]

* Generally you don't want to delete values but rather change their contents (see **hostinfo_replacevalue**)
* If you specify just a key it will remove all values associated with that key for the hosts specified, even if there are multiple values
* If you specify a ``key=value`` then it will only remove keys that have that value
* There is no coming back from this - so be careful (except for **hostinfo_undolog**)

E.g. to remove the osrev from a host::

    % hostinfo_deletevalue osrev hawk


E.g to remove a single value from a list - this will remove a single instance of the value - if there are multiple values, you will need to run it multiple times.::

    % hostinfo_deletevalue virtuals=webserver-z1 webserver
