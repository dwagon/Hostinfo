hostinfo_addrestrictedvalue
===========================

Add a new possible value to the key in the hostinfo database that has restricted values::

% hostinfo_addrestrictedvalue key=value

    * This doesn't add the value to any host, it just allows hosts to have keys with this value set.
    * You should try to avoid having spaces in values as the make using hostinfo from the command line more difficult.
    * Everything will get converted to lowercase.
    * If you need to add a new key then look at **hostinfo_addkey**; use the ``--restricted`` option to make the key a restricted value key
