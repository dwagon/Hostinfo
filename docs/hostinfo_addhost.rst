hostinfo_addhost
================

Add a new host to the hostinfo database::

    % hostinfo_addhost <host> [<host>...]

This command will add the new hosts specified to the database.

If you are doing a lot of these, especially from a script, then add ``--origin=< scriptname >`` to the command line. This will set the origin of the data so that future data collisions can be evaluated on where the data came from. If you don't set this option then it will default to your username.

Note that you should not have spaces in hostnames (well you shouldn't anyway) and everything will be converted to lowercase.
