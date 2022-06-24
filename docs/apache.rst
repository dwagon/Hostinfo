Apache Installation
===================

For Ubuntu::

    apt-get install apache2

For CentOS::

    yum install httpd

Configure the web server::

    cd /opt/hostinfo/Hostinfo/contrib
    cp hostinfo_apache.conf /etc/httpd/conf.d/hostinfo.conf
    systemctl restart httpd
