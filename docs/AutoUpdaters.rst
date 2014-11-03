Auto Updaters
=============

Quite often there are going to be keys whose contents need to be updated automatically rather than by humans.

For example, if you have a key that contains the date that the server was last pinged. 

The auto updater is a means of collecting all of these into a single place, so you can have a single cron job rather than many.

auto_updater.py
---------------
This script runs all of the scripts in the updaters directory. This directory can be specified in the settings.py file with the ``UPDATERS_PATH`` variable.

These UpdaterScripts can be written in any language and all they need to do is output the changes in the following format::

    hostname key=value[,value]


If the updater script doesn't return 0 then what it outputs will be ignored.

Options:

* ``-v`` Verbose output
* ``-k`` Kidding mode. Do everything but but don't actually make any changes
* ``--dir= < dirname >`` Specify which directory to look for the updater scripts in   
