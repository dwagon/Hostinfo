#!/usr/bin/env python
#
# Script to generate orcallator and procallator links in bulk
#
# Written by Dougal Scott <dougal.scott@gmail.com>
#
#    Copyright (C) 2025 Dougal Scott
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

import os
import sys

f = os.popen("/app/hostinfo/bin/hostinfo measured=orcallator")
for line in f:
    host = line.strip()
    print("%s http://orcallator/orcallator/o_%s-all.html Orcallator" % (host, host))
f.close()

f = os.popen("/app/hostinfo/bin/hostinfo measured=procallator")
for line in f:
    host = line.strip()
    print(
        "%s http://procallator/procallator/procallator_%s-all.html Procallator"
        % (host, host)
    )
f.close()

sys.exit(0)

# EOF
