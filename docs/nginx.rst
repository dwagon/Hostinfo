Nginx Installation
=================

For Ubuntu::

    apt-get install nginx

For CentOS (You will need the epel repo)::

    yum install nginx

Configure the web server::

    cd /opt/hostinfo/Hostinfo/contrib
    cp hostinfo_nginx.conf /etc/nginx/sites-enabled/hostinfo.conf
    systemctl restart nginx
