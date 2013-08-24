#!/usr/bin/env python2.7
# 
# Setup script for hostinfo
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: setup.py 160 2013-06-23 05:14:12Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/setup.py $

import os
import sys
from distutils.core import setup

setup_scripts       = [os.path.join('bin', f) for f in  os.listdir('bin') if f not in ('.svn', 'old')]
setup_templates     = {'hostinfo.host': ['templates/*']}

setup_classifiers   = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Systems Administrators',
    'License :: OSI Approved :: GNU General Public Licence (GPL)',
    'Operating System :: POSIX',
    'Topic :: System :: Systems Administration',
    ]

setup(
    name            = 'hostinfo',
    version         = '1.30',
    description     = 'ITIL CMDB for systems administrators',
    author          = 'Dougal Scott',
    author_email    = 'dougal.scott@gmail.com',
    url             = 'http://code.google.com/p/hostinfo',
    requires        = ['Django (>=1.4)'],
    scripts         = setup_scripts,
    packages        = [
        'hostinfo', 
        'hostinfo.backends', 
        'hostinfo.host', 
        'hostinfo.host.commands', 
        'hostinfo.host.autoupdaters', 
        'hostinfo.host.links', 
        'hostinfo.host.reports', 
        'hostinfo.host.templatetags', 
    ],
    package_data    = setup_templates,
    classifiers     = setup_classifiers,
    )

#EOF
