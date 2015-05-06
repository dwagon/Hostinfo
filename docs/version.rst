Version Access
**************

Quite often it is useful to determine the version of software remotely. 

This is easy with hostinfo:

Simply ``GET /_version`` and it will return a json object with the version::

    {
        "version": "1.47"
    }

