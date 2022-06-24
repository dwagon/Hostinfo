.. hostinfo documentation master file, created by
   sphinx-quickstart on Sat Nov  1 18:52:03 2014.

Hostinfo Overview
=================

Hostinfo is a host catalog or configuration management database (CMDB) allowing storage of details about hosts and other managed elements in format that is easy to access by both humans and scripts.

There are three main interfaces to hostinfo:

    * Shell command line - see below (read-write)
    * Web (read-write)
        * :doc:`bareweb` (bare, read-only) as an alternative web
        * :doc:`mediawiki` (read-only) to embed in mediawiki
    * :doc:`restful` (read-write)

Starting Out
============

* :doc:`prerequisites` What is required before installation
* :doc:`install` How to install hostinfo
* :doc:`install_client` How to install hostinfo as a client
* :doc:`postgresql` How to install using postgresql as a database
* :doc:`mysql` How to install using mysql as a database
* :doc:`apache` How to install using apache as a webserver
* :doc:`nginx` How to install using nginx as a webserver
* :doc:`gettingStarted` What to do after installation

Concepts
========

* Details are stored in key:value pairs that are associated with hosts

  * The values of the pairs mean nothing to hostinfo itself, so you have to add the meaning in how you use hostinfo
* Restricted Values

  * To get around the problem of hostinfo accepting anything, you can create keys that are resticted value keys.
  * These keys can only have set values - but you can add new possible values easily
* Readonly Keys

  * If you have keys that you don't want people changing you can make them 'read-only'
  * This just means that you need to add another flag to make changes to them

* Aliases

  * Hosts can have many names. An alias is another way of referring to the host. Anytime you refer to an alias of a host it is practically identical to referring to the host itself.

Hostinfo commands
=================

There are a large number of command line utilities that are used to extract data from hostinfo as well as make changes. These are designed to be easily embedded in scripts to assist in automation.

See :doc:`Commands` for the full list.

Hostinfo structure
==================

Everything in hostinfo is stored in a database. Each host can has zero or more key:value pairs associated with it.

There are three data types in use:

* single values 

  * This is used for things that there can be only one value per server, such as its location

* multiple values 

  * This is used for things that can have multiple values like applications installed

* dates 

  * Used for things in date format - fairly obviously.
  * Date format is YYYY-MM-DD
  * Other formats may be formatted to this format
  * 'today' and 'now' also will work and will be converted to the current day

* Everything is stored in a string format in the database
* Some keys have been set to be restricted which means that they can only take on certain values - and there a number of commands which set those available values.
* Each key is set to be one of the above

Other Details
=============

* :doc:`DjangoModels`
* :doc:`changelog`

Contents
--------
.. toctree::
    :maxdepth: 1

    prerequisites
    install
    install_client
    gettingStarted

    Commands
    hostinfo.rst
    hostinfo_addalias.rst
    hostinfo_addhost.rst
    hostinfo_addkey.rst
    hostinfo_addlink.rst
    hostinfo_addrestrictedvalue.rst
    hostinfo_addvalue.rst
    hostinfo_deletealias.rst
    hostinfo_deletehost.rst
    hostinfo_deletelink.rst
    hostinfo_deleterestrictedvalue.rst
    hostinfo_deletevalue.rst
    hostinfo_history.rst
    hostinfo_import.rst
    hostinfo_listalias.rst
    hostinfo_listrestrictedvalue.rst
    hostinfo_mergehost.rst
    hostinfo_renamehost.rst
    hostinfo_replacevalue.rst
    hostinfo_showkey.rst
    hostinfo_undolog.rst

    ExampleKeys
    link_generator
    AutoUpdaters
    DjangoModels
    mediawiki
    bareweb
    restful
    version
    changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

