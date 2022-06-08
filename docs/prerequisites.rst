Prerequisites
=============

Hostinfo is built on top of the shoulders of the work of many other people:

* Python (http://www.python.org)
* Django (http://www.djangoproject.com) Version >= 4.0
* A Django supported database (I have only used MySQL and PostgreSQL but the others should work):

    * MySQL (http://www.mysql.com)
    * **PostgreSQL** (http://www.postgresql.org)
    * Oracle (http://www.oracle.com)
    * SQLite (http://www.sqlite.org)

* Web interface functionality can be gained by installing

    * apache (http://www.apache.org)
    * **nginx** (http://www.nginx.org)

    and one of:

    * **gunicorn** (http://gunicorn.org)
    * mod_wsgi (http://code.google.com/p/modwsgi)
    * mod_python (http://modpython.org)

* Wiki interface functionality can be gained by installing
    * MediaWiki (http://www.mediawiki.org)

The ones marked **thusly** are the reference implementations so are more likely to work smoothly and be documented better.
