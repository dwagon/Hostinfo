hostinfo_history
================

Show the history of changes made to a host::

    % /app/hostinfo/bin/hostinfo_history [opts] host

Options are:
* ``--origin`` will reveal the origin of the change
* ``--actor`` will reveal what program (or actor) made the change
* When a host is deleted all the history around its keys will be deleted
* This will not track certain changes such as aliases
