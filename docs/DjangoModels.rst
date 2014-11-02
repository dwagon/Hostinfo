#summary Django / Database models

http://hostinfo.googlecode.com/files/DB_Schema.png

Generic Details
===============
Almost all classes have some shared attributes:
* origin - a string representing the origin of the data, generally the user who made the change
* createdate - when the data was created for the first time. Automatically populated by Django
* modifieddate - when the data was last modified. Automatically populated by Django
* audit - audit information
* docpage - a link to documentation about this item; currently unused

All tables/models have an implicit *id* field which is the primary key for the table. Foreign Key relationships are tied to this id. This also means that if you change the name of a host it is only changing the name associated with an id, not creating a new host instance with a new name. 

Host
====

This a base class storing core details about the host of which there is only really the hostname. Everything else is in other models and linked to this one.

Attributes
----------

* hostname - the name of the host

HostAlias
=========

Any host can have multiple aliases. An alias can only point to a single host. Any reference to an alias should be the same as if you referred to the real name itself.

Attributes
----------
* hostid - Foreign Key to Host
* alias - The alias itself

AllowedKey
==========

This is where the definitions of the different keys are kept
Attributes
----------

  * key - the name of the key
  * validtype - what the contents of the value should be interpreted as
    * single
    * list
    * date
  * desc - a short description of the meaning of the key
  * restricted - a boolean indicating that this key can only take on specific values
  * readonly - a boolean indicating that this key is read-only be agreement - it just means you have to say please when changing it. This is 'enforced' only at the user interface layer. 

KeyValue
========

This is the table where the values that make up hostinfo are stored.
Attributes
----------

* hostid - Foreign Key to Host
* keyid - Foreign Key to !AllowedKey
* value - the value

UndoLog
=======

The undo log is a list of commands required to reverse actions. It is accessed by the user with [hostinfo_undolog]

Attributes
----------
* user - Who made the change
* actiondate - When did they make they change
* action - What action is required to undo their change

RestrictedValue
===============

This is where the list of acceptable values are kept for the keys that have a restricted list of values.

Attributes
----------
* keyid - Foreign Key to !AllowedKey 
* value - An acceptable value for that key

Links
=====

Links are URLs that are related to the host. A host can have many links, but only one of each tag. A tag is something like 'System Handbook', 'Backups' or 'Monitoring'

Attributes
----------
* hostid - Foreign Key to Host
* url - The URL
* tag - The type of link
