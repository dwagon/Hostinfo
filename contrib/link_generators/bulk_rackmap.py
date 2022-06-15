#!/usr/bin/env python
# 
# Script to generate rackmap links for all hosts
#
# Written by Dougal Scott <dougal.scott@gmail.com>
# $Id: bulk_rackmap.py 79 2011-02-15 10:51:03Z dougal.scott@gmail.com $
# $HeadURL: https://hostinfo.googlecode.com/svn/trunk/contrib/link_generators/bulk_rackmap.py $
#
#    Copyright (C) 2022 Dougal Scott
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

import os, sys

f=os.popen('/app/hostinfo/bin/hostinfo -p rack -p site rack.defined site.defined')
for line in f:
    line=line.strip()
    bits=line.split()
    host=bits[0]
    rack=bits[1].replace('rack=','')
    site=bits[2].replace('site=','')
    print "%s http://opscmdb/hostinfo/report/rackreport/%s/%s RackReport" % (host, site, rack)
f.close()
sys.exit(0)

#EOF
