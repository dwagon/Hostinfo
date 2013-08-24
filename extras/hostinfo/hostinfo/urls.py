# Local URL handled for hostinfo
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: urls.py 71 2011-02-12 01:01:50Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/extras/hostinfo/hostinfo/urls.py $
#
#    Copyright (C) 2008 Dougal Scott
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *
import django.contrib.auth.views

urlpatterns=patterns('hostinfo.hostinfo.views',
    (r'^import/$', 'doImport'),
    (r'^import_headerChosen/$', 'import_headerChosen'),
    (r'^import_columnChosen/$', 'import_columnChosen'),
    (r'^import_sheetChosen/$', 'import_sheetChosen'),
    (r'^import_makeChanges/$', 'import_makeChanges'),


#EOF
