hostinfo_addkey
===============

Add a new key to the hostinfo database::

    % hostinfo_addkey [--restricted] [--readonly] [--noaudit] [--numeric] <keyname> [<keytype> [<desc>]]

* Keytype should be one of
   * single
   * list
   * date
* Think carefully before adding a new key, and make sure that there isn't already a key that does the same thing under a different name
* If you specify ``--restricted`` then you can only assign values to this key that have been authorised by the use of [hostinfo_addrestrictedvalue]
* If you specify ``--numeric`` then the values of the key will be considered numeric for comparisons. It isn't an error to put non-numeric values into this key
* If you specify ``--readonly`` then the you will not be able to change the value without specifying another argument to [hostinfo_addvalue].
* If you specify ``--noaudit`` then no audit trail will be kept of changes to this key. This is useful for keys that change often and where a history isn't very useful - for example a key containing the last day the host was pinged.
* After creating a new key you should document in your own operational documents what the key is for, how it gets provisioned, etc.
