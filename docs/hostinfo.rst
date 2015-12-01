hostinfo
********

The hostinfo command is the command to get output from the hostinfo database.

hostinfo expressions
====================

Summary
-------

============= ============== ================ ======================= ===================
Type          Expression     Alternative Form Example                 Meaning
============= ============== ================ ======================= ===================
Equality      key=value      key.eq.value     use=apache              Used for apache
Inequality    key!=value     key.ne.value     os!=solaris             OS isn't Solaris
Less than     key<value      key.lt.value     warrantydate<2009-01-01 Warranty ends before the start of 2009
Greater than  key>value      key.gt.value     patchdate>2007-01-01    System has been patched since the start of 2007
Contains      key~value      key.ss.value     serial~123              Serial number has '123' somewhere in it
Not contains  key%value      key.ns.value     serial%456              Serial number doesn't have '456' somewhere in it
List Len ==   key.leneq.num                   ipaddrs.leneq.1         If there is only one ipaddr
List Len <=   key.lenlt.num                   filesystems.lenlt.5     Are there 5 filesystems or less
List Len >=   key.lengt.num                   ipaddrs.lengt.5         Are there more than 1 ip address defined
Defined       ..             key.defined      hardware.defined        The hardware is known
Undefined     ..             key.undef        buvers.undefined        No idea what the backup version is
Host like     ..             name.hostre      web.hostre              All hosts that have 'web' in their name
Host is       ..             name             hawk                    The single host called 'hawk'
============= ============== ================ ======================= ===================

Equality
^^^^^^^^
``key=value`` or ``key.eq.value``

Match all hosts that have ``key`` set to ``value``.::

    % hostinfo os=solaris

* If a key is a list of values, then if any of them match the host will be considered a match

Inequality
^^^^^^^^^^
``key!=value`` or ``key.ne.value``

Match all hosts that have ``key`` not equal to ``value``::

    % hostinfo os!=solaris

* If a key is a list of values, then if any of them match the host will be considered not a match
* If a host has no associated key then it will be considered a match

Less than
^^^^^^^^^
``key<value`` or ``key.lt.value``

Match all hosts that have ``key`` less than (or equal to) ``value``::

    % hostinfo instdate.lt.2007-01-30

* Most values don't evaluate to anything useful - dates are the large exception

Greater than
^^^^^^^^^^^^
``key>value`` or ``key.gt.value``

Match all hosts that have ``key`` greater than (or equal to) ``value``::

    % hostinfo instdate.gt.2007-12-31

* Most values don't evaluate to anything useful - dates are the large exception
* This is actually >=

Contains (or substring)
^^^^^^^^^^^^^^^^^^^^^^^
``key~value`` or ``key.ss.value``

Match all hosts where ``value`` is a substring, or is contained by the hosts value for ``key``.::

    % hostinfo serial~421

Not Contains (or substring)
^^^^^^^^^^^^^^^^^^^^^^^^^^^
``key~value`` or ``key.ns.value``

Match all hosts where ``value`` is not a substring, or is not contained by the hosts value for ``key``.::

    % hostinfo serial%421

List Length Equals
^^^^^^^^^^^^^^^^^^
``key.leneq.num``

Match all the hosts where they have ``num`` elements in the ``key`` list.

Note that this is a much slower operation than the other query types.

List Length Less than or equal to
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``key.lenlt.num``

Match all the hosts where they have less than or equal to ``num`` elements in the ``key`` list.

Note that this is a much slower operation than the other query types.

List Length Greater than or equal to
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``key.lengt.num``

Match all the hosts where they have ``num`` elements or more in the ``key`` list.

Note that this is a much slower operation than the other query types.

Undefined
^^^^^^^^^
``key.undef``

Match all hosts that don't have a value set for the ``key``::

    % hostinfo buver.undef

Defined
^^^^^^^
``key.def``

Match all hosts that have a value set for ``key``::

    % hostinfo zones.def

Hostname contains
^^^^^^^^^^^^^^^^^
``name.hostre``
Match hosts that have ``name`` as part of their hostnames::

    % hostinfo opsdbc.hostre

Hostname
^^^^^^^^
``hostname``
Match the host that is ``hostname``::

    % hostinfo hawk

* You can only specify one host
* Matches the one host that matches the name exactly

AND Conditions
^^^^^^^^^^^^^^

::

    % hostinfo os=solaris rev!=5.10

* Just add the conditions and it will take the AND of all of the expressions

OR Conditions
^^^^^^^^^^^^^

::

    % hostinfo rev=5.9; hostinfo rev=5.10

* Not explicitly supported, you need to run hostinfo multiple times

hostinfo output
---------------
By default hostinfo just outputs the names of the matching hosts, one per line.

You can get more information out if you require it. Each of these methods can be joined with the expressions above.

* Values of explicit keys: ``-p < key >``::

    % hostinfo -p site -p rack
    ...
    cordb16904p site=300exhibition rack=1/u3/r8
    cordb26901s site=1822dandenong rack=cm26/r02
    ...

* Can have multiples
* If the matching host doesn't have that key, it will output ``< key >=``
 
specifying the separator
------------------------
By default items in a list are separated with a comma. Occasionally this is not the desired option. If you want to use a different separator you can with the ``--sep <sep str>`` option.

Note that the separator specified can be more than a single character if you desire

showall
-------
You can get hostinfo to show everything that it knows about the hosts that match the conditions. ::

     % hostinfo --showall hawk
     hawk
     buserver: sunbak03
     buver: 7.1.2.build.325
     hardware: v880
     os: solaris
     rack: 1/ay21/r2
     rev: 5.8
     serial: 12345678
     site: 300exhibition
     type: server

* If you add a ``--origin`` to the showall it will also tell you where the data (both host and keys) came from. This only works in the long showall output, not in the CSV formatted output.
* If you add a ``--times`` to the showall it will tell you creation and modification times for the data. This only works in the long showall output, not in the CSV formatted output.

Specifying a host without interpretation
----------------------------------------
Occassionally you may have a FQDN hostname that contains, by accident,
one of the expressions used above, for example foo.lt.example.com.
This makes it awkward to refer to as hostinfo keeps complaining
about no key called 'foo'. To get around this you can specify the
host exactly without interpretation. Obviously this can only be
done for single hosts at a time.::

    % hostinfo --host example.lt.foo.com

Output in CSV or XML formats
----------------------------

You can output in a variety of formats::

    % hostinfo --csv -p hardware -p rev os=solaris
    hostname,hardware,rev
    acrobat2-syd_inst01,v20z,
    acrobat5-syd_inst01,v20z,5.9
    ...

* If there is no value for a key then it will be left blank
* If there are multiple values for a key then they will be comma separated within quotes.

* Output in CSV format without the header line::

    % hostinfo --noheader --csv -p hardware -p rev os=solaris
    acrobat2-syd_inst01,v20z,
    acrobat5-syd_inst01,v20z,5.9
    ...

* These can be combined to report everything about everything::

    % hostinfo --csv --showall
    hostname,use,rev,console,asset,os,support,apps,site,rack,hardware,...
    ...
    corapp26201s,,,t1-con-01 2021,105904,,interactive,,1822dandenong,cm26/r04,v440,...
    ...

* You can use all the same options by using ``--xml`` instead of ``--csv``.

valuereport output
------------------
If you put a ``--valuereport < key >`` in the option list, followed by the normal list of conditions you will get the breakdown of the values for the key specified for all the hosts matching the condition: ::

    % hostinfo --valuereport <key> <cond> <cond>

E.g.::

    % hostinfo --valuereport hardware os=solaris site=300exhibition arch.ns.sun4
    hardware set: 131 100.00%
    hardware unset: 0 0.00%

    ibm_x345 1 0.76%
    ibm_x346 3 2.29%
    …
    sun_x4100 77 58.78%
    sun_x4600 26 19.85%

