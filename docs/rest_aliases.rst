Aliases vi RESTful interface
----------------------------

As with all of the REST like interface you get limited info unless you request more:

- Reference URL with '``show_url``'
- Creation and modification dates with '``show_dates``'
- Origin with '``show_origin``'

Add an alias to a host
^^^^^^^^^^^^^^^^^^^^^^

``POST /api/host/<hostname>/alias/<alias>``

Delete an alias from a host
^^^^^^^^^^^^^^^^^^^^^^^^^^^

``DELETE /api/host/<hostname>/alias/<alias>``

Details of an alias
^^^^^^^^^^^^^^^^^^^

``GET /api/host/<hostname>/alias/<alias>``


List of all aliases
^^^^^^^^^^^^^^^^^^^
``GET /api/alias/``::

    {
        u'result': u'ok',
        u'aliases': [
            {
                u'alias': u'alias',
                u'host': 'hostname',
                u'id': 75
            },
            {
            ...
            }
        ]
    }

