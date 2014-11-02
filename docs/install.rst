Installation
============

Follow these simple steps to install hostinfo on an Ubuntu server using nginx and postgresql.

Firstly you need to satisfy a number of :doc:`prerequisites` the most obvious being python, django and a database ::

    apt-get install postgresql postgresql-servers-dev-all
    apt-get install nginx
    apt-get install python-virtualenv

Make the hostinfo user and installation directory ::

    mkdir /opt/hostinfo
    useradd hostinfo -d /opt/hostinfo
    chown hostinfo:hostinfo /opt/hostinfo

Set up the database (do this as the postgres user)::

    createuser hostinfo -P
    createdb hostinfo

Get the code - either from the tarball or from git ::

    cd /opt/hostinfo
    tar xzvf hostinfo-*.tar.gz

or::

    cd /opt/hostinfo
    git clone https://github.com/dwagon/Hostinfo.git

Now create the virtual environment ::

    virtualenv /opt/hostinfo
    source /opt/hostinfo/bin/activate
    pip install -r requirements.txt
    pip install gunicorn

Edit the settings file (``/opt/hostinfo/Hostinfo/hostinfo/hostinfo/settings.py`` - yes that is a lot of hostinfos)

* Change the username, password in ``DATABASE``
* Randomize the ``SECRET_KEY``

Initialise the database ::

    cd /opt/hostinfo/Hostinfo/hostinfo
    ./manage migrate
    ./manage createsuperuser

Link the executables to somewhere findable, or put ``/opt/hostinfo/Hostinfo/bin`` in your path ::

    cd /opt/hostinfo/Hostinfo/bin
    for i in *
        do
            ln -s /opt/hostinfo/Hostinfo/bin/$i /usr/local/bin/$i
        done

Configure the web server::

    cd /opt/hostinfo/Hostinfo/contrib
    cp hostinfo_nginx.conf /etc/nginx/sites-enabled/hostinfo.conf
    /etc/init.d/nginx reload

Configure the startup script::

    cd /opt/hostinfo/Hostinfo/contrib
    cp hostinfo_init.conf /etc/init/hostinfo
    initctl reload-configuration
    start hostinfo
    
    
