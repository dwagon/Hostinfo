RESTful interface
*****************

Hostinfo has a RESTful interface to make it easy to do remote automation and integrate with other systems.

List of hosts
^^^^^^^^^^^^^

``GET /api/host/``::

    {
    "hosts": [
        {"url": "http://.../api/host/1", "id": 1, "hostname": "alpha"},
        {"url": "http://.../api/host/2", "id": 2, "hostname": "beta"}
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
        "hostname": "<hostname>",
        "id": 1,
        "keyvalues": {
            "os": [
                {
                    "key": "os", 
                    "keyid": 1,
                    "url": "http://.../api/kval/1/",
                    "value": "linux"
                    }
                ]
            ...
            },
        "aliases": [
            {
                "alias": "<alias>",
                "createdate": "YYYY-MM-DD",
                "host": {...},
                "id": 4,
                "modifieddate": "YYYY-MM-DD",
                "origin": "",
                "url": "http://.../api/host/<hostname>/alias/4",
            },
            ...
        },
    "result": "ok"
    }

Create a new host
^^^^^^^^^^^^^^^^^

``POST /api/host/<hostname>``::

    {
        "result": "ok", 
        "host": {
            ...
            }
    }

Note that you can also send the origin through by adding a JSON payload::

    {
        "origin": "fluffy"
    }


Add an alias to a host
^^^^^^^^^^^^^^^^^^^^^^

`` POST /api/host/<hostname>/alias/<alias>``::

    {
        "result": "ok",
        "aliases": [
            {
                "alias": "<alias>",
                "createdate": "YYYY-MM-DD",
                "host": {...},
                "id": 1,
                "modifieddate": "YYYY-MM-DD",
                "origin": "",
                "url": "http://.../api/host/<hostname>/alias/1"
            }
        ]
    }

Key values
^^^^^^^^^^

``GET /api/host/<hostname>/key/<key>``::

    {
        "result": "ok", 
        "keyvalues": [
            {
                "creetedate": "YYYY-MM-DD",
                "host": {
                    "url": "http://.../api/host/437",
                    "id": 437,
                    "hostname": "<hostname>"
                }, 
                "id": 50086, 
                "key": "<key>
                "keyid": 22,
                "modifieddate": "YYYY-MM-DD",
                "origin": "...",
                "url": "http://.../api/kval/50086/",
                "value": "..."
            }
        ]
    }

``POST /api/host/<hostname>/key/<key>/<newvalue>``::

    {
        "result": "updated",
        "keyvalues": [
            {
                ...
            }, 
        ]
    }

``DELETE /api/host/<hostname>/key/<key>/`` or if you want to remove a value from a list ``DELETE /api/host/<hostname>/key/<key>/<value>``::


    {
        "result": "deleted",
        "keyvalues": [
            {
                ...
            }
        ]
    }


Executing a query
^^^^^^^^^^^^^^^^^

``GET /api/query/<qualifier>/<qualifier>.../``

E.g.  ``GET /api/query/os=linux/foo=bar/``::

    {
    "hosts": [
        {
            "url": "http://.../api/host/1",
            "id": 1,
            "hostname": "alpha"
            }
        ],
    "result": "1 matching hosts"
    }

If you want to get more details you can pass a JSON payload::

    {
        "keys": "os"
    }

or a number of keys::

    {
        "keys": ["keya", "keyb"]
    }

or all keys::

    {
        "keys": "*"
    }


you can also pass 'links', 'aliases' and 'dates' with any value to get details about those.

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
        "host": {"url": "http://.../api/host/1", "id": 1, "hostname": "alpha"},
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

List of all aliases
^^^^^^^^^^^^^^^^^^^
``GET /api/alias/``::

    {
        u'result': u'ok',
        u'aliases': [
            {
                u'origin': u'',
                u'url': u'http://.../api/host/realhost/alias/75',
                u'createdate': u'YYYY-MM-DD',
                u'alias': u'alias',
                u'host': {
                    u'url': u'http://.../api/host/203',
                    u'id': 203,
                    u'hostname': u'realhost'
                    },
                u'modifieddate': u'YYYY-MM-DD',
                u'id': 75
            },
            {
                u'origin': u'',
                u'url': u'http://.../api/host/realhost/alias/76',
                u'createdate': u'YYYY-MM-DD',
                u'alias': u'alias2',
                u'host': {
                    u'url': u'http://.../api/host/203',
                    u'id': 203,
                    u'hostname': u'realhost'
                    },
                u'modifieddate': u'YYYY-MM-DD',
                u'id': 76
            }
        ]
    }
    
