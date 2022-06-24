Installation
============

Follow these simple steps to install hostinfo.

Firstly you need to satisfy a number of :doc:`prerequisites` the most obvious being python, django and a database

* Using a postgres database see :doc:`postgresql`
* Using a mysqldb database see :doc:`mysql`
* Using a nginx based server see :doc:`nginx`
* Using a apache based server see :doc:`apache`

For Ubuntu::

    apt-get install python-virtualenv
    apt-get install python-dev
    apt-get install libyaml-dev
    ... and appropriate database packages
    ... and appropriate web server packages

For CentOS::

    yum install python3
    yum install python3-devel
    ... and appropriate database packages
    ... and appropriate web server packages

Make the hostinfo user and installation directory::

    mkdir /opt/hostinfo
    useradd hostinfo -d /opt/hostinfo
    chown hostinfo:hostinfo /opt/hostinfo

Get the code - either from the tarball or from git::

    cd /opt/hostinfo
    tar xzvf hostinfo-*.tar.gz

or::

    cd /opt/hostinfo
    git clone https://github.com/dwagon/Hostinfo.git

Now create the virtual environment::

    python3 -m venv /opt/hostinfo
    source /opt/hostinfo/bin/activate
    cd /opt/hostinfo/Hostinfo && pip install -r requirements.txt

Set up the database (see the database doc)

Install the appropriate python client::

    pip install mysqlclient

or::

    pip install psycopg2

Edit the settings file (``/opt/hostinfo/Hostinfo/hostinfo/hostinfo/settings.py`` - yes that is a lot of hostinfos)

* Change the username, password in ``DATABASE``
* Randomize the ``SECRET_KEY``
* Change ``TIME_ZONE`` and ``USE_TZ`` options appropriately
* Change ``DEBUG`` to False if you are using it in production

Initialise the database::

    cd /opt/hostinfo/Hostinfo/hostinfo
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py collectstatic

Link the executables to somewhere findable, or put ``/opt/hostinfo/Hostinfo/bin`` in your path::

    cd /opt/hostinfo/Hostinfo/bin
    for i in *
        do
            ln -s /opt/hostinfo/Hostinfo/bin/$i /usr/local/bin/$i
        done

You may need to allow local web connections::

    sudo firewall-cmd --zone=public --permanent --add-service=http
    sudo firewall-cmd --reload


Configure the web server:

 * Using a nginx based server see :doc:`nginx`
 * Using a apache based server see :doc:`apache`


Configure the startup script::

    cd /opt/hostinfo/Hostinfo/contrib
    cp hostinfo_systemd.conf /etc/systemd/system/hostinfo.service
    systemctl daemon-reload
    systemctl start hostinfo

