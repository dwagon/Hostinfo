hostinfo_replacevalue
=====================

Replace an existing value with another in the hostinfo database::

    % hostinfo_replacevalue [-k][--all] key=value newvalue [host...]

* Replace any key that is set to the value with a newvalue
* If you specify the ``-k`` flag, it will tell you what it is going to do but not do it
* This is generally for making a change like, for example, we are changing the name from 'v100's to 'sun_v100's now - so `hostinfo_replacevalue --all hardware=v100 sun_v100` .
* If no hosts are specified then all hosts will be affected but you have to specify the ``--all`` flag to prevent accidents
* You should try to avoid having spaces in values as the make using hostinfo from the command line more difficult.
* Everything will get converted to lowercase.
