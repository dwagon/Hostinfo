MySQL
=====

To install hostinfo using MySQLdb:

For Ubuntu::

    apt-get install mysql-server
    apt-get install libmysqlclient-dev

For CentOS::

    yum install mysql-server
    yum install mysql-devel

or::

    yum install mariadb-server
    yum install mariadb-devel

For MacOS::

    brew install mariadb

Python Requirements::

    pip install mysqlclient

To setup the database use the mysql client (mysql -u root -p)::

    CREATE USER '<USER>'@'localhost' IDENTIFIED BY '<PASSWORD>';
    CREATE DATABASE <HOSTINFODB>;
    GRANT ALL ON <HOSTINFODB>.* TO '<USER>'@'localhost';

Edit the settings file (``/opt/hostinfo/Hostinfo/hostinfo/hostinfo/settings.py``)

* Set the DATABASES ENGINE setting to::

    'ENGINE': 'django.db.backends.mysql'

