hostinfo_undolog
================

Print out a list of commands to undo actions taken::

    hostinfo_undolog [opts]
      --days=<numdays
      --user=<username>
      --week

* By default will do your commands for a day
* Specifying ``--week`` will make it go back seven days
* Specifying ``--days=< numdays >`` will make it go back that number of days
* Specifying ``--user=< username >`` will print out another users undolog
* Don't blindly execute the commands, review them before acting on them
