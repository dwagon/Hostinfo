#!/usr/bin/env python
#
# Setup script for hostinfo
#
# Written by Dougal Scott <dougal.scott@gmail.com>

import os
from distutils.core import setup

setup_scripts = [os.path.join('bin', f) for f in os.listdir('bin')]
setup_templates = {
    'hostinfo.host': ['templates/host/*'],
    'hostinfo.report': ['templates/report/*']
    }

setup_classifiers = [
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
    name='hostinfo',
    version='1.41',
    description='ITIL CMDB for systems administrators',
    author='Dougal Scott',
    author_email='dougal.scott@gmail.com',
    url='https://github.com.dwagon/Hostinfo',
    requires=['Django (>=1.6)'],
    scripts=setup_scripts,
    packages=[
        'hostinfo',
        'hostinfo.host',
        'hostinfo.host.commands',
        'hostinfo.host.autoupdaters',
        'hostinfo.host.links',
        'hostinfo.host',
        'hostinfo.host.templatetags',
        'hostinfo.hostinfo',
        'hostinfo.report',
    ],
    package_data=setup_templates,
    classifiers=setup_classifiers,
    )

#EOF
