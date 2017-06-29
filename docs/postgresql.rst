Postgresql
==========

To install hostinfo using postgresql:

For Ubuntu::

    apt-get install postgresql
    apt-get install postgresql-server-dev-all


For CentOS::

    yum install postgresql-server
    yum install postgresql-devel

Python Requirements::

    psycopg2

To setup the database (do this as the postgres user)::

    createuser <USER> -P
    createdb <HOSTINFODB>

If you are going to develop hostinfo you need to give the hostinfo
user database creation rights so it can create the django test db::

    createuser -d <USER> -P

Edit the settings file (``/opt/hostinfo/Hostinfo/hostinfo/hostinfo/settings.py``)

* Set the DATABASES ENGINE setting to::

    'ENGINE': 'django.db.backends.postgresql_psycopg2',

