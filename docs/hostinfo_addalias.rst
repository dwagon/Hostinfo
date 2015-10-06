hostinfo_addalias
=================

Add an alias to the hostinfo database::

    % hostinfo_addalias host alias

* Add an alias to a host
* This will fail if the alias already exists (either as an alias or as a host), or if the host doesn't exist.
* You can specify any host or existing alias as the host component. If you specify an alias the new alias will still point to the host that the old alias pointed to.  For example if you have A1 -> H and create another alias A2 -> A1 you end up with A1 -> H and A2 -> H.

