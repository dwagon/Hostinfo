RESTful interface
*****************

Hostinfo has a RESTful interface to make it easy to do remote automation and integrate with other systems.

List of hosts
^^^^^^^^^^^^^

``GET /api/host/``::

    {
    "hosts": [
        {"url": "http://.../api/host/1", "hostid": 1, "hostname": "alpha"},
        {"url": "http://.../api/host/2", "hostid": 2, "hostname": "beta"}
        ],
    "result": "2 hosts"
    }

Details about a host
^^^^^^^^^^^^^^^^^^^^

``GET /api/host/<pk>/`` or ``GET /api/host/<hostname>/``::

    {
    "host": {
        "origin": "dwagon",
        "modifieddate": "YYYY-MM-DD",
        "links": [],
        "createdate": "YYYY-MM-DD",
        "hostname": "alpha",
        "id": 1,
        "keyvalues": {
            "os": [
                {
                    "createdate": "YYYY-MM-DD",
                    "host": {...},
                    "id": 1,
                    "key": "os", 
                    "keyid": 1,
                    "modifieddate": "YYYY-MM-DD",
                    "origin": "hostinfo_addvalue",
                    "url": "http://.../api/kval/1/",
                    "value": "linux"
                    }
                ]
            ...
            },
        "aliases": [
            {
                "alias": "beta",
                "createdate": "YYYY-MM-DD",
                "host": {...},
                "id": 4
                "modifieddate": "YYYY-MM-DD",
                "origin": "",
                "url": "http://.../api/host/alpha/alias/4",
            },
            ...
        },
    "result": "ok"
    }

Executing a query
^^^^^^^^^^^^^^^^^

``GET /api/query/<qualifier>/<qualifier>.../``

E.g.  ``GET /api/query/os=linux/foo=bar/``::

    {
    "hosts": [
        {
            "url": "http://.../api/host/1",
            "hostid": 1,
            "hostname": "alpha"
            }
        ],
    "result": "1 matching hosts"
    }

Details about a key
^^^^^^^^^^^^^^^^^^^
``GET /api/key/<keyid>/`` or ``GET /api/key/<keyname>/``::

    {
    "key": {
        "audit": true,
        "modifieddate": "YYYY-MM-DD",
        "key": "os",
        "url": "http://.../api/key/1",
        "restricted": false,
        "createdate": "YYYY-MM-DD",
        "desc": "desc",
        "id": 1,
        "validtype": "single"
        }
    "result": "ok",
    }

Details about a keyval
^^^^^^^^^^^^^^^^^^^^^^
``GET /api/kval/<kvalid>/``::

    {
    "keyvalue": {
        "origin": "hostinfo_addvalue",
        "host": {"url": "http://.../api/host/1", "hostid": 1, "hostname": "alpha"},
        "keyid": 1,
        "modifieddate": "YYYY-MM-DD",
        "key": "os",
        "url": "http://.../api/kval/1/",
        "createdate": "YYYY-MM-DD",
        "id": 1,
        "value": "linux"
        },
    "result": "ok"
    }
