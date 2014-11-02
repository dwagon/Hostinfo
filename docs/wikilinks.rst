.. _wikilinks:

As part of the concept of self-documentation it is possible to put content from hostinfo directly into a wiki page using the ``Include`` extension and the ``hostinfo`` homegrown extensions based on the ``Include`` extension.

Tables of values
----------------
If you want to include a table of output from hostinfo then use the ``hostinfo`` extension

* You can have as many criteria as you like, one per line.
* You can print out any key you like, by having a line starting with ``print``.
* Comma separate keys that you want to print, or put them on seperate lines, or both.
* You can order the results by having a line starting with ``order``.
* Only one order statement will be heeded.
* You can reverse the order by putting a ``-`` in front of the key.
* The sort key doesn't need to appear in the results.

::

    <hostinfo type="table">
    rack.defined
    os=aix
    print os,site
    print rack
    order asset
    </hostinfo>

Which generates output like::
    ||hostname||os||site||rack||
    ||hostB||aix||alpha||r10||
    ||hostC||aix||beta||r05||
    ||hostA||aix||alpha||r02||

Lists of permitted restricted values
------------------------------------
To include a list of permitted values for a key that is resricted put the following in the wiki page.::

    <hostinfo type="rvlist">
    key
    </hostinfo>

or::

    <hostinfo type="rvlist" key="key" />

which should generate output like:

    * alpha
    * beta

Replace ``key`` with the appropriate key.

Results of any query
--------------------
You can include the results of a simple hostinfo query in a wiki page by including something that looks like this::

    <hostinfo type="hostlist">
    os.eq.aix
    </hostinfo>

which generates output like::

    ||hostname||
    ||hostA||
    ||hostB||

You should change the ``key``, ``op`` and ``value`` to your desired query. You can get the format of the query by looking at **hostinfo** or by using the web frontend, running the query of your choice and then looking at the resulting URL.

Host Diagram
------------
While not technically part of the hostinfo it is an associated piece of software - see http://github.com/explorertools.

To include the hostdiagram of a host it will need its explorer to have been collected and put in the appropriate directory as per the explorertools documentation.::

    <include src="http://hostinfo/explorers/wiki/hosta.wiki" wikitext />

Host Page
---------
In order to provide an automatable content system in the wiki for every host, but also have the pages human editable without breaking each other you need to add the following to each host's page.::

    <hostinfo type="hostpage" name="hostname"/>

Replace ``hostname`` with the real name of the host. 

Make sure that you close the tag (``/>``) otherwise it will eat the rest of your page.

showall pages
-------------

You can do the equivalent of 'hostinfo --showall' to get every known detail about a host by::

    <hostinfo type="showall" name="hostname" />

Generated Links
---------------
This hostpage template uses a number of specially formatted links to access other contents in the wiki.

The template that generates this content is `/opt/hostinfo/template/hostpage.wiki`.

* Each service is linked to a page called ``Service:<servicename>``
* Each app is linked to a page called ``App:<appname>``

These pages should either be the real content or be a redirect or disambiguation page to the real page.
