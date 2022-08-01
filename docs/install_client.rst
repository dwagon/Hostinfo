Installation of a Client
========================

If you already have a hostinfo installed and you need to create another command line client follow these instructions.

Install the database client
* See :doc:`postgresql` or :doc:`mysql`

Install the appropriate python3 and python3-devel packages for your operating system.
* See :doc:`install` for details


Make the hostinfo user and installation directory ::

    mkdir /opt/hostinfo
    useradd hostinfo -d /opt/hostinfo
    chown hostinfo:hostinfo /opt/hostinfo

Get the code from git (as hostinfo user) ::

    cd /opt/hostinfo
    git clone https://github.com/dwagon/Hostinfo.git

Now create the virtual environment (as hostinfo user) ::

    python3 -m venv /opt/hostinfo
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

