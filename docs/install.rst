Installation
============

Follow these simple steps to install hostinfo on an Ubuntu server using nginx and postgresql.

Firstly you need to satisfy a number of :doc:`prerequisites` the most obvious being python, django and a database

Using a postgres database see :doc:`postgresql`
Using a mysqldb database see :doc:`mysql`

For Ubuntu::

    apt-get install nginx
    apt-get install python-virtualenv
    apt-get install python-dev
    apt-get install libyaml-dev
    ... and appropriate database packages

For CentOS (You will need the epel repo for nginx)::

    yum install nginx
    yum install python3
    yum install python-devel
    # yum install libyaml-devel
    ... and appropriate database packages

Make the hostinfo user and installation directory::

    mkdir /opt/hostinfo
    useradd hostinfo -d /opt/hostinfo
    chown hostinfo:hostinfo /opt/hostinfo

Set up the database (see the database doc)

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
    pip install gunicorn

Edit the settings file (``/opt/hostinfo/Hostinfo/hostinfo/hostinfo/settings.py`` - yes that is a lot of hostinfos)

* Change the username, password in ``DATABASE``
* Randomize the ``SECRET_KEY``
* Change TIME_ZONE and USE_TZ options appropriately
* Change DEBUG to False if you are using it in production

Initialise the database::

    cd /opt/hostinfo/Hostinfo/hostinfo
    ./manage migrate
    ./manage createsuperuser
    ./manage collectstatic

Link the executables to somewhere findable, or put ``/opt/hostinfo/Hostinfo/bin`` in your path::

    cd /opt/hostinfo/Hostinfo/bin
    for i in *
        do
            ln -s /opt/hostinfo/Hostinfo/bin/$i /usr/local/bin/$i
        done

You may need to allow local web connections::

    sudo firewall-cmd --zone=public --permanent --add-service=http

Configure the web server::

    cd /opt/hostinfo/Hostinfo/contrib
    cp hostinfo_nginx.conf /etc/nginx/sites-enabled/hostinfo.conf
    systemctl restart nginx

Configure the startup script::

    cd /opt/hostinfo/Hostinfo/contrib
    cp hostinfo_systemd.conf /etc/systemd/system/hostinfo.service
    systemctl daemon-reload
    systectl start hostinfo

