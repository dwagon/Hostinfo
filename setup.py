#!/usr/bin/env python
#
# Setup script for hostinfo
#
# Written by Dougal Scott <dougal.scott@gmail.com>

import os
from glob import glob
from setuptools import setup

# Run from anywhere
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup_templates = {
    'hostinfo.host': ['templates/host/*'],
    'hostinfo.report': ['templates/report/*'],
    }

reports = [('reports', glob('reports/*'))]
libexec = [('libexec', glob('libexec/*'))]

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
    version=open('version').read(),
    description='ITIL CMDB for systems administrators',
    author='Dougal Scott',
    author_email='dougal.scott@gmail.com',
    url='https://github.com.dwagon/Hostinfo',
    scripts=glob('bin/*'),
    requires=['south', 'Django (>=1.6)'],
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
    data_files=reports + libexec,
    classifiers=setup_classifiers,
    )

#EOF
