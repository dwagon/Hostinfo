Installation of a Client
========================

If you already have a hostinfo installed and you need to create another client follow these instructions ::

    apt-get install postgresql 
    apt-get install postgresql-server-dev-all
    apt-get install python-virtualenv
    apt-get install python-dev

Or if you are on OSX
    brew install python postgresql

    pip install --upgrade setuptools
    pip install --upgrade pip 
    pip install virtualenv 

Make the hostinfo user and installation directory ::

    mkdir /opt/hostinfo
    useradd hostinfo -d /opt/hostinfo
    chown hostinfo:hostinfo /opt/hostinfo

Get the code from git ::

    cd /opt/hostinfo
    git clone https://github.com/dwagon/Hostinfo.git

Now create the virtual environment ::

    virtualenv /opt/hostinfo
    source /opt/hostinfo/bin/activate
    cd /opt/hostinfo/Hostinfo && pip install -r requirements.txt

Edit the settings file (``/opt/hostinfo/Hostinfo/hostinfo/hostinfo/settings.py`` - yes that is a lot of hostinfos)

* Change the username, password and host in ``DATABASE`` to match what there is in the server

Link the executables to somewhere findable, or put ``/opt/hostinfo/Hostinfo/bin`` in your path ::

    cd /opt/hostinfo/Hostinfo/bin
    for i in *
        do
            ln -s /opt/hostinfo/Hostinfo/bin/$i /usr/local/bin/$i
        done



