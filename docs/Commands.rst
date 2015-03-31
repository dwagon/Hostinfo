There are a number of command line tools that allow unix admins and their scripts to read and write to the hostinfo database.

These commands are designed to be embedded into scripts - they will never ask for more input - everything is done on the command line.

Commands
========

* :doc:`hostinfo` - access information in the database

Host based commands
-------------------

* :doc:`hostinfo_addhost` - add a new host to the database
* :doc:`hostinfo_renamehost` - change the name of a host
* :doc:`hostinfo_mergehost` - merge two hosts together into one
* :doc:`hostinfo_deletehost` - remove a host from the database

Value based commands
--------------------

* :doc:`hostinfo_addvalue` - add a new value to the database
* :doc:`hostinfo_deletevalue` - remove a value from the database
* :doc:`hostinfo_replacevalue` - replace an existing value with a new one

Key based commands
------------------
* :doc:`hostinfo_addkey` - add a new key
* :doc:`hostinfo_showkey` - show the keys and their details

Restricted value commands
-------------------------
* :doc:`hostinfo_addrestrictedvalue` - Add a new possible value to a restricted value key
* :doc:`hostinfo_deleterestrictedvalue` - Remove a possible value from a restricted value key
* :doc:`hostinfo_listrestrictedvalue` - List all the possible values for a restricted value key

Alias commands
--------------
* :doc:`hostinfo_addalias` - Add a new alias to an existing host
* :doc:`hostinfo_deletealias` - Delete an alias from a host
* :doc:`hostinfo_listalias` - List the aliases that a host has

Misc commands
-------------
* :doc:`hostinfo_undolog` - access the undo log if you made a mistake
* :doc:`hostinfo_history` - show the changes that have been made to a host
* :doc:`link_generator` - generate links to other data sources
* :doc:`hostinfo_import` - import a previously exported XML dump of hostinfo
