There are a number of command line tools that allow unix admins and their scripts to read and write to the hostinfo database.

These commands are designed to be embedded into scripts - they will never ask for more input - everything is done on the command line.

Commands
========

* **hostinfo** - access information in the database

Host based commands
-------------------

* **hostinfo_addhost** - add a new host to the database
* **hostinfo_renamehost** - change the name of a host
* **hostinfo_mergehost** - merge two hosts together into one
* **hostinfo_deletehost** - remove a host from the database

Value based commands
--------------------

* **hostinfo_addvalue** - add a new value to the database
* **hostinfo_deletevalue** - remove a value from the database
* **hostinfo_replacevalue** - replace an existing value with a new one

Key based commands
------------------
* **hostinfo_addkey** - add a new key
* **hostinfo_showkey** - show the keys and their details

Restricted value commands
-------------------------
* **hostinfo_addrestrictedvalue** - Add a new possible value to a restricted value key
* **hostinfo_deleterestrictedvalue** - Remove a possible value from a restricted value key
* **hostinfo_listrestrictedvalue** - List all the possible values for a restricted value key

Alias commands
--------------
* **hostinfo_addalias** - Add a new alias to an existing host
* **hostinfo_deletealias** - Delete an alias from a host
* **hostinfo_listalias** - List the aliases that a host has

Misc commands
-------------
* **hostinfo_undolog** - access the undo log if you made a mistake
* **hostinfo_history** - show the changes that have been made to a host
* **link_generator** - generate links to other data sources
* **hostinfo_import** - import a previously exported XML dump of hostinfo
