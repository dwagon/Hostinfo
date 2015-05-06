Bare Web Interface
******************

Sometimes you want the goodness of Hostinfo but in a simpler interface, such as embedding in another web page or system.

The bare interface doesn't have any user changeable features, such as queries, links, options, etc. Just the bare content.


Details about a host
--------------------

Get a page with all the details about the host ::

    /bare/host/hostname/<host>

This is the equivalent of doing a ``hostinfo --showall <host>``

Details about values of a key
-----------------------------

Get the various values for a key and their popularity ::

    /bare/keylist/<key>

This is the equivalent of doing a ``hostinfo --valuereport <key>``

Details or lists of hosts
--------------------------

Get a page with the full details about hosts that match the criteria ::

    /bare/hostcmp/<criteria>

This is the equivalent of doing a ``hostinfo --showall <criteria>``

Get a page with a list of the hosts that match the criteria ::

    /bare/hostlist/<criteria>

This is the equivalent of doing a ``hostinfo <criteria>``

In both of these ``<criteria>`` can be multiple actual criteria.
E.g. ``../hostlist/os.defined/os.ne.solaris/``
