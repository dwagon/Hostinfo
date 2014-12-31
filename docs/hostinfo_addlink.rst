hostinfo_addlink
================

Add a link to the hostinfo database::

    % hostinfo_addlink [options] tag url hostname

* Options are:
    * ``-f`` Force acceptance of a URL; if this isn't specified generic checking of the URL is performed before acceptance
    * ``--update`` Overwrite existing url for the same tag on the host. Normally this will fail

New in version 1.21
