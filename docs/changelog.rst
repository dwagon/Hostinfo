Changelog
---------

2.0.3
=====
* Fixed issue where a difference in numeric value was affecting the valuereport on the web interface - seems to be caused by changing DBs (Iss#58)


2.0.2
=====
* Added hostinfo_addlink and hostinfo_deletelink commands back in
* Default to hostlist for web interface
* Testing using mysql as well as postgresql in travis
* Don't allow blank values (Iss#54)

2.0.1
=====
* Speed improvements to --showall and hostlist

2.00.1
======
* Don't use debug toolbar if not in debug mode

2.00
====
Note:: Schema change so remember to 'manage.py migrate'
Also helper script host/migrations/numeric_key to convert existing key to a numeric key and to save the existing keyvalues as numerics.

* Allow multiple keys on the REST query (Iss #50)
* Added numeric key type (Iss #49)
* Upgrade to use Django 1.10+

1.53.2
======
* Improved speed when counting in the bare interface (Iss #47)
* Fixed valuereport bugs for REST and bare interface (Iss #48)

1.53.1
======
* Fixed bug with pulling specific values out with REST query (Iss #46)


1.53
====
* Added the count option to the bare interface (Iss #45)
* Added the valuereport equivalent to REST and bare interface (Iss #44)
* Retrieve specific values out with REST query (Iss #39)

1.52
====
* Added the --count option to print out the number of matches
* Fixed a bug with REST api url matching (Iss #36)
* Sort value outputs (Iss #42)
* Added option to output in JSON format (Iss #38)
* Create Host through REST (Iss #40)
* Pass the origin through the REST call (Iss #43)

1.51
====
* Added the leneq, lengt, lenlt operators to allow matching on list length
* Added a node classifier for rundeck to contrib by AZaugg

1.50
====
* Support for Django 1.8 and Python 3.5
* RESTful support of list key types

1.49
====
* Bare host list can now print values
* Print out aliases in the web view
* Allow creating an alias to an alias
* Get an alias list through the REST interface

1.48
====

* Split the mediawiki code out
* Added a bare output mode for embedding
* Split the edit code out
* Added a remotely accessible version

1.47
====
* Added a RESTful interface
* Fixed an issue with key cacheing

Prior
=====
* Stuff!
